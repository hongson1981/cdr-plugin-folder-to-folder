import React, { useState } from "react";
import GWButton            from "../components/buttons/GWButton";
import * as APIService     from "../services/Services";
import * as Utils          from "../services/Utils";
import GWDialog            from  "../components/Modal/GWDialog";




export default function Processing(props) {

  const [show, setState]                                       = useState(false);
  const [output, setOutput]                                    = useState("");
  const [showStatusModal, setStatusModal]                      = useState(false);
  const [dialogContent, setDialogContent]                      = useState(null);
  const [loadFileLoader, showLoadFileLoader]                   = useState(false);
  const [startProcessingLoader, showStartProcessingLoader]     = useState(false);
  const [stopProcessingLoader, showStoptProcessingLoader]      = useState(false);
  const [cleanLoader, showCleanLoader]                         = useState(false);
  const [statusLoader, showStatusLoader]                       = useState(false);
  
 

  const startProcessing = () => {
    showStartProcessingLoader(true);
    APIService.callAPIPost(Utils.API_URL+Utils.START_PROCESSING, '', props.threadCount)
    .then(data => {
      showStartProcessingLoader(false);
      setState(true);
      if(data != "Loop stopped"){
        setOutput( Utils.getCurrentDateAndTime() + data + '\r\n' + output )
        props.showSuccessAlert("Processing completed successfully")
      }else{
        setOutput( Utils.getCurrentDateAndTime() + "Processing stopped done" + '\r\n' + output )
      
      }
      
    }).catch(error=>{
      console.log("error" + error);
      showStartProcessingLoader(false);
      props.setError(error.message)
  });
  }

  const stopProcessing = () => {
    setState(true);
    showStoptProcessingLoader(true);
    APIService.callAPIPost(Utils.API_URL+Utils.STOP_PROCESSING)
    .then(data => {
      showStoptProcessingLoader(false);
      setOutput( Utils.getCurrentDateAndTime() + data + '\r\n' + output )
      props.showSuccessAlert("Stopped successfully")
    }).catch(error=>{
      console.log("error" + error);
      showStoptProcessingLoader(false);
      props.setError(error.message)
  });
  }

  const loadFiles = () => {
    showLoadFileLoader(true);
    APIService.callAPIPost(Utils.API_URL+Utils.LOAD_FILES)
    .then(data => {
      setOutput( Utils.getCurrentDateAndTime() + "PreProcessing is done " + '\r\n' + output )
      showLoadFileLoader(false);
      setState(true);
      props.showSuccessAlert("PreProcessing completed successfully")
    }).catch(error=>{
      console.log("error" + error);
      showLoadFileLoader(false);
      props.setError(error.message)
  });
  }

  const clearData = () => {
    setState(true);
    showCleanLoader(true);
    APIService.callAPIPost(Utils.API_URL+Utils.CLEAN_DATA_STATUS)
    .then(data => {
      showCleanLoader(false);
      setOutput( Utils.getCurrentDateAndTime() + data.message + '\r\n' + output )
      props.showSuccessAlert("Clear Data And Status Folders Successfully")
    }).catch(error=>{
      console.log("error" + error);
      showCleanLoader(false);
      props.setError(error.message)
  });
  }
 
 const displayStatus=()=>{
  showStatusLoader(true)
  APIService.callAPIGet(Utils.API_URL + Utils.API_STATUS_PATH)
  .then(data => {
    setStatusModal(true)
    setDialogContent(data);
    showStatusLoader(false)
  }).catch(error=>{
      console.log("error" + error);
      showStatusLoader(false);
      props.setError(error.message)
  });
 }

 const cleanOuputArea=()=>{
    setOutput("");
 }
 
  return (
    
    <div>
      <h3 className="heading-title">Processing</h3>
      <div className="card-holder">
        {show ?
          <div className="output-result cdr-output " id="processingOutput">
            <h4>Output <button onClick={cleanOuputArea} id="reloadOutput" className="reload-output">&times;</button></h4>
            <textarea
              rowsmax       ={4}
              aria-label    ="maximum height"
              value         = {output}
              className     ="form-control"
            />
          </div> : <div></div>}
        <div className="buttons-group action-buttons">
          <GWButton showLoader={loadFileLoader} callback={loadFiles}       text={"Load Files"}         classname={"start-processing"} />
          <GWButton showLoader={startProcessingLoader} callback={startProcessing}  text={"Start Processing"}   classname={"stop-processing"} />
          <GWButton showLoader={stopProcessingLoader} callback={stopProcessing}   text={"Stop Processing"}    classname={"load-files"} />
          <GWButton showLoader={cleanLoader} callback={clearData}        text={"Clear Data"}         classname={"clear-data"} />
          <GWButton showLoader={statusLoader} callback={displayStatus}     text={"Status"}         classname={"status-button"} />
        </div>
        <GWDialog  title ={"Processing Status"} content={dialogContent} onClose={() => {setStatusModal(false);  setDialogContent(null)}} show={showStatusModal}/>
      </div>
    </div>
  );
}




