import React, { useState } from "react";
import GWButton from "../components/buttons/GWButton";
import * as APIService from "../services/Services";
import * as Utils from "../services/Utils";
import GWDialog from "../components/Modal/GWDialog";
import swal from 'sweetalert';



export default function Configuration(props) {

  const [cloudSDKIPs, setCloudISDKPs] = useState("[]");
  const [formatedCloudISDKPs, setFormatedCloudISDKPs] = useState("[]");
  const [threadCount, setThreadCount] = useState(props.threadCount);
  const [showConfigModal, setConfigModal] = useState(false);
  const [dialogContent, setDialogContent] = useState(null);
  const [baseDir, setBaseDir] = useState(localStorage.getItem(Utils.LS_KEY_BASEDIR));
  const [sdkPort, setSDKPort] = useState(localStorage.getItem(Utils.LS_KEY_SDK_PORT) ? localStorage.getItem(Utils.LS_KEY_SDK_PORT) : Utils.SDK_DEFAULT_PORT);
  const [lastSavedSDKPort, setLastSavedSDKPort] = useState(localStorage.getItem(Utils.LS_KEY_SDK_PORT) ? localStorage.getItem(Utils.LS_KEY_SDK_PORT) : Utils.SDK_DEFAULT_PORT);





  React.useEffect(() => {
    props.showLoader(true);
    
    APIService.callAPIGet(Utils.SDK_SERVER_IPS + Utils.LOAD_CLOUD_SDK_IPS)
      .then(data => {
        setCloudISDKPs(JSON.stringify(data.live_ips));
        appendPort(data.live_ips, lastSavedSDKPort);
        showLoader(false);

      }).catch(error => {
        console.log("error" + error);
        props.setError(error.message)
        showLoader(false);
      });

  }, []);

  React.useEffect(() => {
    cloudSDKIPs && appendPort(JSON.parse(cloudSDKIPs), sdkPort);
  }, [sdkPort]);



  const appendPort = (cloudSDKIPObject, port) => {
    let plugin_ips = cloudSDKIPObject.map(itm => {
      let obj = itm + ':' + port
      return obj
    })
    setFormatedCloudISDKPs(JSON.stringify(plugin_ips))
  }

  const showLoader = (show) => {
    props.showLoader(show);
  }

  const loadFromAWSAPICallback = (data, isError) => {
    if (data != null && !isError) {
      setCloudISDKPs(JSON.stringify(data.live_ips));
      appendPort(data.live_ips, Utils.SDK_DEFAULT_PORT);
      setSDKPort(Utils.SDK_DEFAULT_PORT);
      setLastSavedSDKPort(Utils.SDK_DEFAULT_PORT);
      localStorage.setItem(Utils.LS_KEY_SDK_PORT, Utils.SDK_DEFAULT_PORT);
    } else {
      props.setError(data.message)
    }
    showLoader(false);
  }

  const handleIPsChangeHandler = (event) => {
    setCloudISDKPs(event.target.value);
  }

  const loadFromAWSCallback = () => {
    showLoader(true);
    APIService.callAPIGetAsync(Utils.SDK_SERVER_IPS + Utils.LOAD_CLOUD_SDK_IPS, loadFromAWSAPICallback);
  }

  const setPlugInCallback = () => {

    if (cloudSDKIPs == "[]") {
      swal("Set Plugin IPs failed", "Cannot update the Plugin IPS. SDK IPs are not set '.", "error");
      returnl
    }
    showLoader(true);
   
    APIService.callAPIPost(Utils.API_URL + Utils.SET_PLUGIN_IPS,
       { "Endpoints": Utils.getEndPoints(cloudSDKIPs, sdkPort) })
      .then(data => {

        if (data.Endpoints) {
          props.showSuccessAlert("Successfully set")
          setLastSavedSDKPort(sdkPort)
          localStorage.setItem(Utils.LS_KEY_SDK_PORT, sdkPort);
        } else {
          props.setError(data.detail)
          setSDKPort(lastSavedSDKPort);
        }
        showLoader(false);

      }).catch(error => {
        c//onsole.log("error" + error);
        showLoader(false);
        props.setError(error.message)
      });

  }
  const onThreadChange = (event) => {
    setThreadCount(event.target.value);
    props.setThreadCount(event.target.value);
    localStorage.setItem(Utils.LS_KEY_THREAD_COUNT, event.target.value);

  }

  const baseDirHandler = () => {
    //console.log(event.target.value)
    var sel = document.getElementById('baseDirSelect');
    showLoader(true);
    let baseDirs = {
      "hd1_path": "./test_data/" + sel.value + "/hd1",
      "hd2_path": "./test_data/" + sel.value + "/hd2",
      "hd3_path": "./test_data/" + sel.value + "/hd3"
    }

    localStorage.setItem(Utils.LS_KEY_BASEDIR, sel.value);
    setBaseDir(sel.value);
    APIService.callAPIPost(Utils.API_URL + Utils.API_CONFIGURE_ENV, baseDirs)
      .then(data => {
        showLoader(false);
        props.showSuccessAlert("Successfully Configured")
      }).catch(error => {
        console.log("error" + error);
        showLoader(false);
        props.setError(error.message)
      });
  }


  const displayConfig = () => {
    APIService.callAPIGet(Utils.API_URL + Utils.API_CONFIG_PATH)
      .then(data => {
        setConfigModal(true)
        setDialogContent(data)
      }).catch(error => {
        console.log("error" + error);
        showLoader(false);
        props.setError(error.message)
      });
  }

  const resetConfig = () => {
    localStorage.setItem(Utils.LS_KEY_THREAD_COUNT, 25);
    localStorage.setItem(Utils.LS_KEY_BASEDIR, Utils.TEST_DATA[0]);
    localStorage.setItem(Utils.LS_KEY_SDK_PORT, Utils.SDK_DEFAULT_PORT);
    setLastSavedSDKPort(Utils.SDK_DEFAULT_PORT)
    setBaseDir(Utils.TEST_DATA[0]);
    setThreadCount(25);
    setSDKPort(Utils.SDK_DEFAULT_PORT)
    props.setThreadCount(25);


  }

  const updateBaseDir = (element) => {
    setBaseDir(element.target.value)
  }

  const setCloudSDKPort = () => {
    swal('Cloud SDK Port', {
      content: {
        element: "input",
        attributes: {
          placeholder: "Enter cloud sdk port",
          value: sdkPort
        },
      }
    })
      .then((value) => {
        if (value != null && value != "" && !isNaN(Number(value))) {
          setSDKPort(value);

        }

      });
  }

  return (
    <div>
      <h3 className="heading-title">Configuration</h3>
      <div className="card-holder">
        <button onClick={displayConfig} id="viewConfigButton" className="view-config">View Config</button>
        <button onClick={resetConfig} id="resetConfigButton" className="view-config">Reset</button>
        <GWDialog title={"Server Configurartion"} content={dialogContent} onClose={() => { setConfigModal(false); setDialogContent(null) }} show={showConfigModal} />

        <div className="cdr-left">
          <h4>
            Cloud SDK IPs
            <button onClick={setCloudSDKPort} id="editPortButton">
              <i className="fa fa-edit"></i>
              Edit Port</button>

          </h4>

          <input
            type="text"
            placeholder="[ ]"
            value={formatedCloudISDKPs && formatedCloudISDKPs.replace(/,/g, ", ")}
            id="setCloudIps"
            className="form-control"
            onChange={handleIPsChangeHandler}
          />
          <div className="buttons-group sdk-buttons">
            <GWButton showLoader={false} text={"Load from AWS"} callback={loadFromAWSCallback} classname="start-processing" />

            <div className="setPluginIps">
              <GWButton showLoader={false} text="Set Plugin IPs" callback={setPlugInCallback} classname="stop-processing" />

            </div>
          </div>
        </div>

        <div className="cdr-left cdr-second">
          <div className="middle-cdr">
            <div className="middle-cdr-cont">
              <button onClick={baseDirHandler} >Set base dir</button>
              <div className="dropboxdiv">
                <select
                  type="text"
                  placeholder=""
                  id="baseDirSelect"
                  className="form-control dropbox_scenario"
                  value={baseDir}
                  onChange={updateBaseDir}
                >
                  {
                    Utils.TEST_DATA.map((folder, index) => {
                      return <option key={index} value={folder}>{folder}</option>
                    })
                  }


                </select>
                <div className="select-icon">
                  <svg className="icon" viewBox="0 0 20 20">
                    <path fill="none" d="M11.611,10.049l-4.76-4.873c-0.303-0.31-0.297-0.804,0.012-1.105c0.309-0.304,0.803-0.293,1.105,0.012l5.306,5.433c0.304,0.31,0.296,0.805-0.012,1.105L7.83,15.928c-0.152,0.148-0.35,0.223-0.547,0.223c-0.203,0-0.406-0.08-0.559-0.236c-0.303-0.309-0.295-0.803,0.012-1.104L11.611,10.049z"></path>
                  </svg>
                </div>
              </div>
            </div>
            <div className="threads-count">
              <label>Threads:</label>
              <input
                type="text"
                placeholder="25"
                value={threadCount}
                className="form-control"
                onChange={onThreadChange}
              />
            </div>
          </div>
        </div>
        <div className="clear"></div>
      </div>


    </div>
  );
}




