"""
analytics/s3_uploader.py

Uploads Allure HTML reports to AWS S3 after each pipeline run.
Uses AWS free tier — S3 gives 5GB free storage.

Secrets are fetched from AWS SSM Parameter Store (Standard tier = free).
Never hardcode keys — always fetch from SSM at runtime.

Interview talking point:
  "I store all sensitive keys in AWS SSM Parameter Store — it is free for
  standard parameters. boto3 fetches them at runtime. The code never
  has a hardcoded key. Even if the repo is public, secrets are safe."

Usage:
  python analytics/s3_uploader.py --bucket my-bucket --report-dir allure-report --build-id 42
"""
import os
import argparse
import boto3
from pathlib import Path
from datetime import datetime


def get_secret_from_ssm(param_name: str, region: str = "ap-south-1") -> str:
    """
    Fetch a secret from AWS SSM Parameter Store (free tier).
    Use SecureString for sensitive values.

    Why SSM over Secrets Manager:
      SSM Standard parameters = free.
      Secrets Manager = $0.40/secret/month. Not needed for this use case.
    """
    ssm = boto3.client("ssm", region_name=region)
    response = ssm.get_parameter(Name=param_name, WithDecryption=True)
    return response["Parameter"]["Value"]


def upload_report_to_s3(
    bucket: str,
    report_dir: str,
    build_id: str,
    region: str = "ap-south-1",
) -> str:
    """
    Upload Allure report folder to S3.
    Returns the public URL of the report index.html

    S3 path structure:
      s3://{bucket}/reports/{YYYY-MM-DD}/{build_id}/index.html
    """
    s3 = boto3.client("s3", region_name=region)
    report_path = Path(report_dir)
    date_prefix = datetime.now().strftime("%Y-%m-%d")
    s3_prefix = f"reports/{date_prefix}/{build_id}"

    uploaded = 0
    for file in report_path.rglob("*"):
        if file.is_file():
            relative = file.relative_to(report_path)
            s3_key = f"{s3_prefix}/{relative}"

            content_type = _get_content_type(file.suffix)

            s3.upload_file(
                str(file),
                bucket,
                s3_key,
                ExtraArgs={"ContentType": content_type},
            )
            uploaded += 1

    print(f"Uploaded {uploaded} files to s3://{bucket}/{s3_prefix}/")

    report_url = f"https://{bucket}.s3.{region}.amazonaws.com/{s3_prefix}/index.html"
    print(f"Report URL: {report_url}")
    return report_url


def _get_content_type(suffix: str) -> str:
    types = {
        ".html": "text/html",
        ".js": "application/javascript",
        ".css": "text/css",
        ".json": "application/json",
        ".png": "image/png",
        ".svg": "image/svg+xml",
    }
    return types.get(suffix.lower(), "application/octet-stream")


def store_report_metadata(
    bucket: str,
    build_id: str,
    report_url: str,
    region: str = "ap-south-1",
):
    """
    Store report metadata in SSM Parameter Store for easy retrieval.
    Allows other systems (Jira, Slack) to fetch the latest report URL.
    """
    ssm = boto3.client("ssm", region_name=region)
    ssm.put_parameter(
        Name=f"/langgraph/reports/latest",
        Value=report_url,
        Type="String",
        Overwrite=True,
    )
    print(f"Stored latest report URL in SSM: /langgraph/reports/latest")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--bucket", required=True)
    parser.add_argument("--report-dir", required=True)
    parser.add_argument("--build-id", required=True)
    parser.add_argument("--region", default=os.getenv("AWS_DEFAULT_REGION", "us-east-1"))
    args = parser.parse_args()

    url = upload_report_to_s3(
        bucket=args.bucket,
        report_dir=args.report_dir,
        build_id=args.build_id,
        region=args.region,
    )
    store_report_metadata(
        bucket=args.bucket,
        build_id=args.build_id,
        report_url=url,
        region=args.region,
    )
