import React, { useState }  from "react";
import LoaderBlocking       from  "../components/Loader/LoaderBlocking";
import Configuration        from "./Configuration"
import Processing           from "./Processing"
import Dashboard            from "./Dashboard";



export default function Workflow() {

  const [loader, showLoader]                  = useState(false);
  const [showErrrorMessage, setErrorMessage]  = useState("");
  const [showError, setShowError]             = useState(false);
  const [threadCount, setThreadCount]         = useState(25);
  const [showSuccess, setShowSuccess]         = useState(false);
  const [successMessage, setSuccessMessage]   = useState("");
  
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




