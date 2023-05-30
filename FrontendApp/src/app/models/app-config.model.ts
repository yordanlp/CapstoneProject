export interface IAppConfig {
  env: {
    name: string;
  };
  appInsights: {
    instrumentationKey: string;
  };
  logging: {
    console: boolean;
    appInsights: boolean;
  };
  aad: {
    requireAuth: boolean;
    tenant: string;
    clientId: string;

  };
  apiServer: {
    metadata: string;
    rules: string;
    host: string;
  };
}
