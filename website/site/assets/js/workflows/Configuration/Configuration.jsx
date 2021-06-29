import React, { useState } from "react";
import * as APIService from "../../services/Services";
import * as Utils from "../../services/Utils";
import CloudSDK from "./Components/CloudSDK";
import Scenarios from "./Components/Scenerios";
import ThreadCount from "./Components/Others";
import LoaderBlocking       from  "../../components/Loader/LoaderBlocking";



export default function Configuration(props) {

  const [threadCount, setThreadCount] = useState(props.threadCount);
 
  
  const onThreadChange = (count) => {
    setThreadCount(count);
    props.setThreadCount(count);
    localStorage.setItem(Utils.LS_KEY_THREAD_COUNT, count);

  }

 
  const resetConfig = () => {
    localStorage.setItem(Utils.LS_KEY_THREAD_COUNT, 25);
    localStorage.setItem(Utils.LS_KEY_BASEDIR, Utils.TEST_DATA[0]);
    localStorage.setItem(Utils.LS_KEY_SDK_PORT, Utils.SDK_DEFAULT_PORT);
    setLastSavedSDKPort(Utils.SDK_DEFAULT_PORT)
    setThreadCount(25);

  }


  return (
    <div>
      <br></br>
        {/* <button onClick={displayConfig} id="viewConfigButton" className="view-config">View Config</button> */}
        {/* <button onClick={resetConfig} id="resetConfigButton" className="view-config">Reset</button> */}
        <br></br>
        <CloudSDK showLoader={props.showLoader} setError={props.setError} showSuccessAlert={props.showSuccessAlert}/>
        <Scenarios showLoader={props.showLoader} setError={props.setError} showSuccessAlert={props.showSuccessAlert} />
        <ThreadCount threadCount={threadCount} setThreadCount ={onThreadChange}/>
        <div className="clear"></div>
     
    </div>
  );
}




