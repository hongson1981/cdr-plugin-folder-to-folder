import * as params from '@params';


export const  API_URL               = params.api_url
export const  DASHBOARD_URL         = params.kibana
export const SDK_SERVER_IPS         = "https://1bycqgpa8j.execute-api.eu-west-1.amazonaws.com/prod" 

export const LOAD_CLOUD_SDK_IPS     = "/sdk-servers/ip_addresses"
export const SET_PLUGIN_IPS         = "/configuration/configure_gw_sdk_endpoints";
export const API_CONFIG_PATH        = "/configuration/config/";
export const API_CONFIGURE_ENV      = "/configuration/configure_env/";
export const API_CONFIGURE_SCENARIOS = "/configuration/test_data_folders/";


export const LOAD_FILES             = "/pre-processor/pre-process"
export const START_PROCESSING       = "/processing/start?thread_count=";
export const STOP_PROCESSING        = "/processing/stop";
export const API_STATUS_PATH        = "/processing/status"
export const CLEAN_DATA_STATUS      = "/pre-processor/clear-data-and-status";

export const LS_KEY_BASEDIR         = 'basedir1';
export const LS_KEY_THREAD_COUNT    = 'threadcount1';
export const LS_KEY_SDK_PORT        = 'cloudsdkport1';
export const LS_KEY_VOLUME_TYPE     = 'volumetype1';
export const LS_KEY_SDK_IP          = 'sdkip1'

export const VOLUME_DEFAULT         = 'default'
export const VOLUME_CUSTOM          = 'custom'
export const VOLUME_HD1             = 'hd1'
export const VOLUME_HD2             = 'hd2'
export const VOLUME_HD3             = 'hd3'
export const SDK_DEFAULT_PORT       = '80'




export const TEST_DATA=["scenario-1","scenario-2"]
export const getCurrentDateAndTime=()=>{

    let dateObj = new Date()
    return dateObj.toLocaleDateString("en-US") + "- " + dateObj.toLocaleTimeString("en-US") + ": ";
}


export const getEndPoints =(cloudSDKIPs, sdkPort)=>{
    let cloudSDKIPObject = JSON.parse(cloudSDKIPs);
    let plugin_ips = cloudSDKIPObject.map(itm => {
      let obj = { "IP": itm, "Port": sdkPort }
      return obj
    })
    return plugin_ips;
}