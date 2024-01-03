import * as cdk from 'aws-cdk-lib';
import { Construct } from 'constructs';
import * as lambda from "aws-cdk-lib/aws-lambda";
import * as certificatemanager from "aws-cdk-lib/aws-certificatemanager";
import * as apigateway from "aws-cdk-lib/aws-apigateway";
import { ApiGatewayToLambda } from "@aws-solutions-constructs/aws-apigateway-lambda";
import { Constants } from "./constants";
import * as path from "node:path";

export class FreeMarketFandangoApiStack extends cdk.Stack {
  constructor(scope: Construct, id: string, props?: cdk.StackProps) {
    super(scope, id, props);

    const certificate = certificatemanager.Certificate.fromCertificateArn(this, 'Certificate', Constants.certificateArn);

    new ApiGatewayToLambda(this, 'API', {
      lambdaFunctionProps: {
        runtime: lambda.Runtime.PYTHON_3_10,
        handler: 'free-market-fandango-api.main.handler',
        code: lambda.Code.fromAsset( path.join(__dirname, '../lambda.zip') ),
        timeout: cdk.Duration.seconds(15),
        environment: {
          ADMIN_PASSWORD: process.env.ADMIN_PASSWORD || '',
          SECRET_KEY: process.env.SECRET_KEY || '',
          SPOTIPY_CLIENT_ID: process.env.SPOTIPY_CLIENT_ID || '',
          SPOTIPY_CLIENT_SECRET: process.env.SPOTIPY_CLIENT_SECRET || '',
          SPOTIPY_REDIRECT_URI: process.env.SPOTIPY_REDIRECT_URI || ''
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
  }
}
