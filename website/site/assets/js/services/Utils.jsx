import * as params from '@params';


export const  API_URL               = params.api_url
export const  DASHBOARD_URL         = params.kibana
export const SDK_SERVER_IPS         = "https://tmol8zkg3c.execute-api.eu-west-1.amazonaws.com/prod" 

export const LOAD_CLOUD_SDK_IPS     = "/sdk-servers/ip_addresses"
export const SET_PLUGIN_IPS         = "/configuration/configure_gw_sdk_endpoints";
export const API_CONFIG_PATH        = "/configuration/config/";
export const API_CONFIGURE_ENV      = "/configuration/configure_env/";

export const LOAD_FILES             = "/pre-processor/pre-process"
export const START_PROCESSING       = "/processing/start?thread_count=";
export const STOP_PROCESSING        = "/processing/stop";
export const API_STATUS_PATH        = "/processing/status"
export const CLEAN_DATA_STATUS      = "/pre-processor/clear-data-and-status";

export const LS_KEY_BASEDIR         = 'basedir';
export const LS_KEY_THREAD_COUNT    = 'threadcount';
export const LS_KEY_SDK_PORT        = 'cloudsdkport';
export const SDK_DEFAULT_PORT       = '8080'



export const TEST_DATA=["scenario-1","scenario-2"]
export const getCurrentDateAndTime=()=>{

    let dateObj = new Date()
    return dateObj.toLocaleDateString("en-US") + "- " + dateObj.toLocaleTimeString("en-US") + ": ";
}