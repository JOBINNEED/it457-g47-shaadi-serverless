#!/usr/bin/env bash
# Delete the whole PoC after grading. Irreversible: asks you to type the account ID first.
# Order: API -> functions -> tables -> bucket -> log groups -> roles -> resource group -> budget.
set -uo pipefail
source "$(dirname "$0")/_config.sh"
ACCOUNT=$(aws sts get-caller-identity --query Account --output text)
BUCKET="it457-g47-shaadi-$ACCOUNT"
echo "This permanently deletes the Shaadi PoC in account $ACCOUNT ($REGION)."
read -r -p "Type the account ID to continue: " ok
[ "$ok" = "$ACCOUNT" ] || { echo "Cancelled."; exit 1; }

for id in $(aws apigatewayv2 get-apis --region "$REGION" \
            --query "Items[?starts_with(Name,'shaadi')].ApiId" --output text); do
  aws apigatewayv2 delete-api --region "$REGION" --api-id "$id" && echo "deleted API $id"
done
for fn in "${ALL_FUNCTIONS[@]}"; do
  aws lambda delete-function --region "$REGION" --function-name "$fn" && echo "deleted function $fn"
done
for t in Interests verdicts; do
  aws dynamodb delete-table --region "$REGION" --table-name "$t" >/dev/null && echo "deleted table $t"
done
aws s3 rm "s3://$BUCKET" --recursive --quiet && aws s3api delete-bucket --bucket "$BUCKET" --region "$REGION" \
  && echo "deleted bucket $BUCKET"
for lg in $(aws logs describe-log-groups --region "$REGION" --log-group-name-prefix /aws/lambda/shaadi \
            --query 'logGroups[].logGroupName' --output text); do
  aws logs delete-log-group --region "$REGION" --log-group-name "$lg" && echo "deleted log group $lg"
done
for role in $(aws iam list-roles --query "Roles[?starts_with(RoleName,'shaadi')].RoleName" --output text); do
  for p in $(aws iam list-role-policies --role-name "$role" --query PolicyNames --output text); do
    aws iam delete-role-policy --role-name "$role" --policy-name "$p"; done
  for arn in $(aws iam list-attached-role-policies --role-name "$role" --query 'AttachedPolicies[].PolicyArn' --output text); do
    aws iam detach-role-policy --role-name "$role" --policy-arn "$arn"; done
  aws iam delete-role --role-name "$role" && echo "deleted role $role"
done
aws resource-groups delete-group --region "$REGION" --group it457-g47-shaadi-project >/dev/null 2>&1 \
  && echo "deleted resource group"
aws budgets delete-budget --account-id "$ACCOUNT" --budget-name it457-g47-5usd 2>/dev/null && echo "deleted budget"
echo "Done. IAM users kavya and venkat were not touched; remove them in the IAM console if no longer needed."
