import React, { useState }  from "react";
import LoaderBlocking       from  "../components/Loader/LoaderBlocking";
import Configuration        from "./Configuration"
import Processing           from "./Processing"
import Dashboard            from "./Dashboard";
import * as Utils       from "js/services/Utils";



export default function Workflow() {

  const [loader, showLoader]                  = useState(false);
  const [errorMessage, setErrorMessage]       = useState("");
  const [showError, setShowError]             = useState(false);
  const [threadCount, setThreadCount]         = useState(
        localStorage.getItem(Utils.LS_KEY_THREAD_COUNT)!=null?
          localStorage.getItem(Utils.LS_KEY_THREAD_COUNT):25);
  const [showSuccess, setShowSuccess]         = useState(false);
  const [successMessage, setSuccessMessage]   = useState("");
  
  React.useEffect(() => {
   }, []);
 
  const closeSuccessAlert=()=>{
    setShowSuccess(false);
 }

 const showSuccessAlert=(message)=>{
    setShowSuccess(true)
    setSuccessMessage(message)
    setTimeout(function(){ closeSuccessAlert() }, 3000);
 }


 const closeErrorAlert=()=>{
  setShowError(false); 
  setErrorMessage("")
 }
 const setError=(message)=>{
    setShowError(true); 
    setErrorMessage(message)
 } 

 const setThreadChangeHandler=(thread)=>{
   console.log("setThreadChangeHandler" + thread)
    setThreadCount(thread)
 }

  return (
    
    <div>
        {
          loader && <LoaderBlocking></LoaderBlocking>
        }
        {
        showError &&
        <div 
          id        ="alertBar" 
          className ="alert alert-danger alert-dismissible fade in" 
          >
        <button 
            id          ="closeAlert" 
            className   ="close" 
            data-dismiss="alert" 
            aria-label  ="close"
            onClick     ={closeErrorAlert}
            >&times;</button>
        <strong>
          <img src="/images/fire.png" alt="error" />
          </strong>
        <p id="errortext" >{errorMessage}</p> 
        </div>
        }
       
       {showSuccess &&
        <div 
        id=        "alertSuccess" 
        className= "alert alert-success alert-dismissible fade in" 
        >
          <button 
              id="closeAlertSuccess" 
              className="close" S
              data-dismiss="alert" 
              aria-label="close"
              onClick={closeSuccessAlert}
              >&times;
          </button>
          <strong>
            <img src="/images/checked.png" alt="error" />
          </strong>
          <p id="successtext" >{successMessage}</p> 
      </div>
       }
      <Configuration showLoader={showLoader} setError={setError} showSuccessAlert={showSuccessAlert} threadCount={threadCount} setThreadCount ={setThreadChangeHandler}/>
      <Processing  setError={setError}   showSuccessAlert={showSuccessAlert} threadCount={threadCount} />
      <Dashboard/>
    </div>
  );
}




