import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as certificatemanager from "aws-cdk-lib/aws-certificatemanager";
import * as apigateway from "aws-cdk-lib/aws-apigateway";
import * as dynamodb from "aws-cdk-lib/aws-dynamodb";
import { ApiGatewayToLambda } from "@aws-solutions-constructs/aws-apigateway-lambda";
import { Constants } from "./constants";
import * as path from "node:path";

export class FreeMarketFandangoApiStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const table = new dynamodb.TableV2(this, 'FreeMarketFandango', {
      partitionKey: { name: 'PK', type: dynamodb.AttributeType.STRING },
      sortKey: { name: 'SK', type: dynamodb.AttributeType.STRING },
      removalPolicy: cdk.RemovalPolicy.DESTROY,
    });

    const certificate = certificatemanager.Certificate.fromCertificateArn(this, 'Certificate', Constants.certificateArn);

    const apiGatewayToLambda = new ApiGatewayToLambda(this, 'API', {
      lambdaFunctionProps: {
        runtime: lambda.Runtime.PYTHON_3_10,
        handler: 'free-market-fandango-api.main.handler',
        code: lambda.Code.fromAsset( path.join(__dirname, '../free-market-fandango-api'), {
          bundling: {
            image: lambda.Runtime.PYTHON_3_10.bundlingImage,
            command: [
              'bash', '-c', 'pip install -r requirements.txt -t /asset-output && cp -au . /asset-output'
            ],
          },
        }),
        timeout: cdk.Duration.seconds(15),
        environment: {
          ADMIN_PASSWORD: process.env.ADMIN_PASSWORD || '',
          SECRET_KEY: require('crypto').randomBytes(64).toString('hex'),
          SPOTIPY_CLIENT_ID: process.env.SPOTIPY_CLIENT_ID || '',
          SPOTIPY_CLIENT_SECRET: process.env.SPOTIPY_CLIENT_SECRET || '',
          SPOTIPY_REDIRECT_URI: process.env.SPOTIPY_REDIRECT_URI || '',
          TABLE_NAME: table.tableName,
        },
      },
      apiGatewayProps: {
        restApiName: this.stackName,
        defaultCorsPreflightOptions: {
          allowOrigins: [ `https://${Constants.frontendDomainName}` ],
          allowMethods: [ 'GET', 'PUT', 'POST', 'DELETE' ]
        },
        domainName: {
          domainName: Constants.apiDomainName,
          certificate: certificate,
        },
        defaultMethodOptions: {
          authorizationType: apigateway.AuthorizationType.NONE
        }
      }
    });

    table.grantReadWriteData(apiGatewayToLambda.lambdaFunction);
  }
}
