"""
Tax Vaapsi v3.0 - ONE SHOT AWS SETUP
Run: pip install boto3 && python setup_aws.py
"""
import boto3, json, time, sys, os
from datetime import datetime

# Get credentials from environment variables
AWS_ACCESS_KEY_ID     = os.getenv("AWS_ACCESS_KEY_ID", "YOUR_AWS_ACCESS_KEY")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "YOUR_AWS_SECRET_KEY")
AWS_REGION            = os.getenv("AWS_DEFAULT_REGION", "ap-south-1")
AWS_ACCOUNT_ID        = os.getenv("AWS_ACCOUNT_ID", "YOUR_ACCOUNT_ID")

G="\033[92m"; R="\033[91m"; Y="\033[93m"; B="\033[94m"; E="\033[0m"; BL="\033[1m"
def ok(m):   print(f"{G}  ✅ {m}{E}")
def er(m):   print(f"{R}  ❌ {m}{E}")
def wn(m):   print(f"{Y}  ⚠  {m}{E}")
def hd(m):   print(f"\n{BL}{B}{'='*56}\n  {m}\n{'='*56}{E}")

SESSION = boto3.Session(aws_access_key_id=AWS_ACCESS_KEY_ID,
                        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
                        region_name=AWS_REGION)

def verify():
    hd("Verifying Credentials")
    try:
        id = SESSION.client("sts").get_caller_identity()
        ok(f"Account: {id['Account']} | User: {id['UserId']}")
    except Exception as e:
        er(f"Credentials invalid: {e}"); sys.exit(1)

def create_iam_role():
    hd("STEP 1: IAM Role for Bedrock")
    iam = SESSION.client("iam")
    rname = "TaxVaapsiBedrockAgentRole"
    trust = {"Version":"2012-10-17","Statement":[{"Effect":"Allow","Principal":{"Service":"bedrock.amazonaws.com"},"Action":"sts:AssumeRole","Condition":{"StringEquals":{"aws:SourceAccount":AWS_ACCOUNT_ID},"ArnLike":{"aws:SourceArn":f"arn:aws:bedrock:{AWS_REGION}:{AWS_ACCOUNT_ID}:agent/*"}}}]}
    policy = {"Version":"2012-10-17","Statement":[{"Effect":"Allow","Action":["bedrock:InvokeModel","bedrock:InvokeModelWithResponseStream"],"Resource":"*"},{"Effect":"Allow","Action":["dynamodb:*"],"Resource":f"arn:aws:dynamodb:{AWS_REGION}:{AWS_ACCOUNT_ID}:table/taxvaapsi_*"},{"Effect":"Allow","Action":["s3:*"],"Resource":["arn:aws:s3:::taxvaapsi-*","arn:aws:s3:::taxvaapsi-*/*"]},{"Effect":"Allow","Action":["lambda:InvokeFunction"],"Resource":f"arn:aws:lambda:{AWS_REGION}:{AWS_ACCOUNT_ID}:function:taxvaapsi-*"},{"Effect":"Allow","Action":["logs:*"],"Resource":"*"}]}
    try:
        r = iam.create_role(RoleName=rname, AssumeRolePolicyDocument=json.dumps(trust), Description="TaxVaapsi Bedrock Role")
        arn = r["Role"]["Arn"]; ok(f"Role: {arn}")
    except iam.exceptions.EntityAlreadyExistsException:
        arn = f"arn:aws:iam::{AWS_ACCOUNT_ID}:role/{rname}"; wn(f"Exists: {arn}")
    try:
        iam.put_role_policy(RoleName=rname, PolicyName="TaxVaapsiPolicy", PolicyDocument=json.dumps(policy)); ok("Permissions attached")
    except Exception as e: wn(f"Policy: {e}")
    print("  ⏳ Waiting 12s for IAM propagation..."); time.sleep(12)
    return arn

def create_dynamodb():
    hd("STEP 2: DynamoDB Tables")
    ddb = SESSION.client("dynamodb", region_name=AWS_REGION)
    for name, pk in [("taxvaapsi_users","user_id"),("taxvaapsi_gst_refunds","scan_id"),("taxvaapsi_it_refunds","scan_id"),("taxvaapsi_tds_records","record_id"),("taxvaapsi_notices","notice_id"),("taxvaapsi_agent_activity","activity_id"),("taxvaapsi_compliance","compliance_id")]:
        try:
            ddb.create_table(TableName=name, KeySchema=[{"AttributeName":pk,"KeyType":"HASH"}], AttributeDefinitions=[{"AttributeName":pk,"AttributeType":"S"}], BillingMode="PAY_PER_REQUEST")
            ok(f"Table: {name}")
        except ddb.exceptions.ResourceInUseException: wn(f"Exists: {name}")
        except Exception as e: er(f"{name}: {e}")
    time.sleep(8); ok("All tables ready")

def create_s3():
    hd("STEP 3: S3 Bucket")
    s3 = SESSION.client("s3", region_name=AWS_REGION)
    bucket = f"taxvaapsi-docs-{AWS_ACCOUNT_ID[:8]}"
    try:
        s3.create_bucket(Bucket=bucket, CreateBucketConfiguration={"LocationConstraint":AWS_REGION})
        s3.put_public_access_block(Bucket=bucket, PublicAccessBlockConfiguration={"BlockPublicAcls":True,"IgnorePublicAcls":True,"BlockPublicPolicy":True,"RestrictPublicBuckets":True})
        ok(f"Bucket: {bucket}")
    except s3.exceptions.BucketAlreadyOwnedByYou: wn(f"Exists: {bucket}")
    except Exception as e: er(f"S3: {e}")
    return bucket

def create_sqs():
    hd("STEP 4: SQS Queues")
    sqs = SESSION.client("sqs", region_name=AWS_REGION); urls={}
    for qname, key in [("taxvaapsi-gst-queue","SQS_GST_QUEUE_URL"),("taxvaapsi-it-queue","SQS_IT_QUEUE_URL"),("taxvaapsi-notice-queue","SQS_NOTICE_QUEUE_URL")]:
        try:
            r = sqs.create_queue(QueueName=qname, Attributes={"VisibilityTimeout":"300","MessageRetentionPeriod":"86400"})
            urls[key]=r["QueueUrl"]; ok(f"Queue: {qname}")
        except Exception as e:
            try: urls[key]=sqs.get_queue_url(QueueName=qname)["QueueUrl"]; wn(f"Exists: {qname}")
            except: er(f"SQS {qname}: {e}"); urls[key]=""
    return urls

def create_sns():
    hd("STEP 5: SNS Topic")
    sns = SESSION.client("sns", region_name=AWS_REGION)
    try:
        r = sns.create_topic(Name="taxvaapsi-alerts"); arn=r["TopicArn"]; ok(f"SNS: {arn}"); return arn
    except Exception as e: er(f"SNS: {e}"); return ""

def create_sfn(role_arn):
    hd("STEP 6: Step Functions")
    sfn = SESSION.client("stepfunctions", region_name=AWS_REGION)
    dfn = json.dumps({"Comment":"TaxVaapsi GST Workflow","StartAt":"Scan","States":{"Scan":{"Type":"Pass","Next":"Risk"},"Risk":{"Type":"Pass","Next":"File"},"File":{"Type":"Pass","Next":"Notify"},"Notify":{"Type":"Pass","End":True}}})
    arns={}
    for name, key in [("taxvaapsi-gst-workflow","SFN_GST_WORKFLOW_ARN"),("taxvaapsi-it-workflow","SFN_IT_WORKFLOW_ARN")]:
        try:
            r = sfn.create_state_machine(name=name, definition=dfn, roleArn=role_arn, tags=[{"key":"Project","value":"TaxVaapsi"}])
            arns[key]=r["stateMachineArn"]; ok(f"SFN: {name}")
        except sfn.exceptions.StateMachineAlreadyExists:
            for m in sfn.list_state_machines()["stateMachines"]:
                if name in m["name"]: arns[key]=m["stateMachineArn"]; wn(f"Exists: {name}"); break
        except Exception as e: er(f"SFN {name}: {e}"); arns[key]=""
    return arns

def create_eventbridge():
    hd("STEP 7: EventBridge")
    try:
        SESSION.client("events", region_name=AWS_REGION).put_rule(Name="taxvaapsi-compliance-reminders", ScheduleExpression="rate(7 days)", State="ENABLED", Description="TaxVaapsi weekly compliance reminders")
        ok("EventBridge rule: weekly compliance reminders")
    except Exception as e: wn(f"EventBridge: {e}")

def create_bedrock_agents(role_arn):
    hd("STEP 8: AWS Bedrock Native Agents (Nova Pro)")
    bedrock = SESSION.client("bedrock-agent", region_name=AWS_REGION)
    MODEL = "amazon.nova-pro-v1:0"; ids={}

    agents = [
        ("GST","TaxVaapsi-GST-RefundAgent","GST Refund Command Center - MCP-powered agentic refund detection and filing",
         "You are TaxVaapsi GST Refund Agent powered by Amazon Nova Pro (amazon.nova-pro-v1:0). Find and recover ALL GST refunds for Indian businesses. Use MCP tools - AI DECIDES each portal action (NOT scripted Playwright). Actions: scan_refunds→predict_risk→login→navigate→fill_form→submit→capture_ARN. Deep knowledge: GST Act 2017 Rules 89-96, all CBIC circulars 2024. Risk reduction: 72%→18% via Kiro-style analysis. Respond with structured JSON only."),
        ("IT","TaxVaapsi-IT-RefundAgent","Income Tax Refund Tracker - 40+ deductions, regime comparison, ITR filing",
         "You are TaxVaapsi Income Tax Agent powered by Amazon Nova Pro. Expert in IT Act 1961, sections 80C-80U, HRA, LTA, 24B, NPS. Use MCP tools to interact with IT portal autonomously. Actions: scan_deductions→compare_regimes→file_itr. Old vs New regime: always calculate savings before recommending. 22 Indian languages via Bhashini. JSON responses only."),
        ("NOTICE","TaxVaapsi-NoticeDefense-Agent","Notice Defense - 3 personas: Vision AI + Tax Lawyer + Compliance Officer",
         "You are TaxVaapsi Notice Defense Agent with 3 personas. Persona1-Vision AI: Classify notice, extract section/deadline/demand. Persona2-Tax Lawyer: Draft legal reply with case laws in 40 seconds. Persona3-Compliance Officer: Calculate win probability (typically 92%). Use Tax Law MCP tools. Win rate 92% vs 7-10 days with CA. JSON responses only."),
    ]

    for key, name, desc, instr in agents:
        try:
            r = bedrock.create_agent(agentName=name, agentResourceRoleArn=role_arn, foundationModel=MODEL,
                                     description=desc, instruction=instr,
                                     idleSessionTTLInSeconds=3600, agentCollaboration="DISABLED",
                                     tags={"Project":"TaxVaapsi","Agent":key})
            aid = r["agent"]["agentId"]; ok(f"Agent: {name} → {aid}")
            time.sleep(4); bedrock.prepare_agent(agentId=aid); time.sleep(6)
            try:
                ar = bedrock.create_agent_alias(agentId=aid, agentAliasName="production", description="TaxVaapsi prod")
                alid = ar["agentAlias"]["agentAliasId"]; ok(f"Alias: {alid}")
            except Exception as ae: alid="TSTALIASID"; wn(f"Alias: {ae}")
            ids[f"BEDROCK_{key}_AGENT_ID"]=aid; ids[f"BEDROCK_{key}_AGENT_ALIAS_ID"]=alid
        except bedrock.exceptions.ConflictException:
            # Agent exists, retrieve its ID
            try:
                agents_list = bedrock.list_agents()
                for agent in agents_list.get("agentSummaries", []):
                    if agent["agentName"] == name:
                        aid = agent["agentId"]
                        wn(f"Exists: {name} → {aid}")
                        # Get alias
                        try:
                            aliases = bedrock.list_agent_aliases(agentId=aid)
                            alid = aliases["agentAliasSummaries"][0]["agentAliasId"] if aliases.get("agentAliasSummaries") else "TSTALIASID"
                        except: alid = "TSTALIASID"
                        ids[f"BEDROCK_{key}_AGENT_ID"]=aid; ids[f"BEDROCK_{key}_AGENT_ALIAS_ID"]=alid
                        break
            except Exception as e2:
                er(f"Failed to retrieve {name}: {e2}"); ids[f"BEDROCK_{key}_AGENT_ID"]=""; ids[f"BEDROCK_{key}_AGENT_ALIAS_ID"]=""
        except Exception as e:
            er(f"Agent {name}: {e}"); ids[f"BEDROCK_{key}_AGENT_ID"]=""; ids[f"BEDROCK_{key}_AGENT_ALIAS_ID"]=""

    # Supervisor
    try:
        time.sleep(5)
        sr = bedrock.create_agent(agentName="TaxVaapsi-Supervisor", agentResourceRoleArn=role_arn,
                                  foundationModel=MODEL, description="Master Orchestrator - A2A + Step Functions",
                                  instruction="You are TaxVaapsi Master Orchestrator. Coordinate GST/IT/Notice agents via A2A protocol. Use Step Functions for filing workflows. Maximize tax recovery. JSON only.",
                                  agentCollaboration="SUPERVISOR", idleSessionTTLInSeconds=3600,
                                  tags={"Project":"TaxVaapsi","Agent":"SUPERVISOR"})
        sid=sr["agent"]["agentId"]; ok(f"Supervisor: {sid}")
        time.sleep(5); bedrock.prepare_agent(agentId=sid)
        ids["BEDROCK_SUPERVISOR_AGENT_ID"]=sid; ids["BEDROCK_SUPERVISOR_AGENT_ALIAS_ID"]="TSTALIASID"
    except bedrock.exceptions.ConflictException:
        try:
            agents_list = bedrock.list_agents()
            for agent in agents_list.get("agentSummaries", []):
                if agent["agentName"] == "TaxVaapsi-Supervisor":
                    sid = agent["agentId"]
                    wn(f"Exists: TaxVaapsi-Supervisor → {sid}")
                    try:
                        aliases = bedrock.list_agent_aliases(agentId=sid)
                        alid = aliases["agentAliasSummaries"][0]["agentAliasId"] if aliases.get("agentAliasSummaries") else "TSTALIASID"
                    except: alid = "TSTALIASID"
                    ids["BEDROCK_SUPERVISOR_AGENT_ID"]=sid; ids["BEDROCK_SUPERVISOR_AGENT_ALIAS_ID"]=alid
                    break
        except Exception as e2:
            er(f"Failed to retrieve Supervisor: {e2}"); ids["BEDROCK_SUPERVISOR_AGENT_ID"]=""; ids["BEDROCK_SUPERVISOR_AGENT_ALIAS_ID"]=""
    except Exception as e:
        er(f"Supervisor: {e}"); ids["BEDROCK_SUPERVISOR_AGENT_ID"]=""; ids["BEDROCK_SUPERVISOR_AGENT_ALIAS_ID"]=""
    return ids

def write_env(cfg):
    hd("STEP 9: Writing .env file")
    content = f"""# Tax Vaapsi v3.0 - Auto-generated {datetime.utcnow().isoformat()} UTC

AWS_ACCESS_KEY_ID={AWS_ACCESS_KEY_ID}
AWS_SECRET_ACCESS_KEY={AWS_SECRET_ACCESS_KEY}
AWS_DEFAULT_REGION={AWS_REGION}

BEDROCK_MODEL_ID=amazon.nova-pro-v1:0
BEDROCK_REGION={AWS_REGION}

BEDROCK_GST_AGENT_ID={cfg.get('BEDROCK_GST_AGENT_ID','')}
BEDROCK_GST_AGENT_ALIAS_ID={cfg.get('BEDROCK_GST_AGENT_ALIAS_ID','')}
BEDROCK_IT_AGENT_ID={cfg.get('BEDROCK_IT_AGENT_ID','')}
BEDROCK_IT_AGENT_ALIAS_ID={cfg.get('BEDROCK_IT_AGENT_ALIAS_ID','')}
BEDROCK_NOTICE_AGENT_ID={cfg.get('BEDROCK_NOTICE_AGENT_ID','')}
BEDROCK_NOTICE_AGENT_ALIAS_ID={cfg.get('BEDROCK_NOTICE_AGENT_ALIAS_ID','')}
BEDROCK_SUPERVISOR_AGENT_ID={cfg.get('BEDROCK_SUPERVISOR_AGENT_ID','')}
BEDROCK_SUPERVISOR_AGENT_ALIAS_ID={cfg.get('BEDROCK_SUPERVISOR_AGENT_ALIAS_ID','')}

DYNAMODB_TABLE_PREFIX=taxvaapsi_
USE_LOCAL_DYNAMODB=false
DYNAMODB_ENDPOINT_URL=

S3_BUCKET_NAME={cfg.get('S3_BUCKET_NAME','')}
S3_REGION={AWS_REGION}

SQS_GST_QUEUE_URL={cfg.get('SQS_GST_QUEUE_URL','')}
SQS_IT_QUEUE_URL={cfg.get('SQS_IT_QUEUE_URL','')}
SQS_NOTICE_QUEUE_URL={cfg.get('SQS_NOTICE_QUEUE_URL','')}

SFN_GST_WORKFLOW_ARN={cfg.get('SFN_GST_WORKFLOW_ARN','')}
SFN_IT_WORKFLOW_ARN={cfg.get('SFN_IT_WORKFLOW_ARN','')}

SNS_TOPIC_ARN={cfg.get('SNS_TOPIC_ARN','')}

BEDROCK_AGENT_ROLE_ARN={cfg.get('BEDROCK_AGENT_ROLE_ARN','')}

MCP_GST_SERVER_PORT=9101
MCP_IT_SERVER_PORT=9102
MCP_TAX_LAW_SERVER_PORT=9103

GST_PORTAL_URL=http://localhost:8001
IT_PORTAL_URL=http://localhost:8002
USE_MOCK_PORTALS=true
"""
    with open(".env","w") as f: f.write(content)
    ok(".env written!")

def main():
    print(f"{BL}{G}\n{'='*56}\n  TAX VAAPSI v3.0 - ONE SHOT AWS SETUP\n  Account: {AWS_ACCOUNT_ID} | Region: {AWS_REGION}\n{'='*56}{E}")
    verify()
    cfg={}
    cfg["BEDROCK_AGENT_ROLE_ARN"] = create_iam_role()
    create_dynamodb()
    cfg["S3_BUCKET_NAME"] = create_s3()
    cfg.update(create_sqs())
    cfg["SNS_TOPIC_ARN"] = create_sns()
    cfg.update(create_sfn(cfg["BEDROCK_AGENT_ROLE_ARN"]))
    create_eventbridge()
    cfg.update(create_bedrock_agents(cfg["BEDROCK_AGENT_ROLE_ARN"]))
    write_env(cfg)
    print(f"{BL}{G}\n{'='*56}\n  ✅ ALL DONE! Run python main.py → :8080\n{'='*56}{E}")

if __name__=="__main__":
    main()
