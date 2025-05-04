#  Tree API - Serverless Tree Data Structure Manager

This is a production-ready serverless API for managing tree data structures using AWS Lambda, DynamoDB, Redis (ElastiCache), and API Gateway. It supports node creation and fetching entire trees with caching for performance.

---

##  API Endpoints

### `GET /api/tree`
Fetches the full tree structure.

####  Example response:
```json
[
  {
    "id": "uuid-root",
    "label": "root",
    "children": [
      {
        "id": "uuid-child",
        "label": "child node",
        "children": []
      }
    ]
  }
]
```

---

### `POST /api/tree`
Adds a new node under a specified parent.

####  Request body:
```json
{
  "label": "New Node",
  "parentId": "abc123" // or null if it's a root
}
```

####  Example response:
```json
{
  "message": "Node created",
  "item": {
    "id": "uuid-generated-id",
    "label": "New Node",
    "parentId": "abc123"
  }
}
```

---

##  Deployment Instructions

###  Prerequisites
- Terraform
- AWS account with permissions to create:
  - Lambda Functions
  - DynamoDB Tables
  - API Gateway routes
  - ElastiCache clusters
- AWS credentials (via `~/.aws/credentials` or environment variables)
- Zipped Lambda function code at `../lambda.zip`

### 1. Initialize Terraform
```bash
terraform init
```

### 2. Apply the infrastructure
```bash
terraform apply
```

Terraform will prompt for confirmation and then provision all required resources. Upon success, it will output the HTTP endpoint URL for the API.

---

##  Running Unit Tests

###  Setup
Make sure you have Python 3.10+ and `pip` installed. Then install test dependencies:
```bash
pip install pytest boto3 redis
```

###  Run Tests
```bash
pytest tests/
```

Unit tests mock out AWS and Redis dependencies using `unittest.mock`.

---

## Project Structure
```
.
├── lambda/
│   └── handler.py             # Lambda function code
├── tests/
│   └── test_handler.py        # Unit tests with pytest
├── terraform/
│   ├── main.tf                # Terraform infrastructure
│   └── variables.tf           # Terraform variables
├── lambda.zip                 # Zipped Lambda for deployment
└── README.md
```
