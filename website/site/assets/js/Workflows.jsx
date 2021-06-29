import React, { useState }      from "react";
import * as ReactDOM            from "react-dom";
import PropTypes                from 'prop-types';
import { makeStyles }           from '@material-ui/core/styles';
import AppBar                   from '@material-ui/core/AppBar';
import Tabs                     from '@material-ui/core/Tabs';
import Tab                      from '@material-ui/core/Tab';
import Typography               from '@material-ui/core/Typography';
import Box                      from '@material-ui/core/Box';
import Paper                    from '@material-ui/core/Paper';

import * as params              from '@params';//to load any variable passed from template to your JS files
import Configuration            from './workflows/Configuration/Configuration'
import Processing               from "./workflows/Processing"
import Dashboard                from "./workflows/Dashboard";
import * as Utils               from "./services/Utils";
import LoaderBlocking           from "./components/Loader/LoaderBlocking";
import GWDialog                 from "./components/Modal/GWDialog";
import * as APIService          from "./services/Services";



function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`simple-tabpanel-${index}`}
      aria-labelledby={`simple-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box p={3}>
          <Typography>{children}</Typography>
        </Box>
      )}
    </div>
  );
}

TabPanel.propTypes = {
  children: PropTypes.node,
  index: PropTypes.any.isRequired,
  value: PropTypes.any.isRequired,
};

function a11yProps(index) {
  return {
    id: `simple-tab-${index}`,
    'aria-controls': `simple-tabpanel-${index}`,
  };
}

const useStyles = makeStyles((theme) => ({
  root: {
    flexGrow: 1
  },
}));




const Workflows= ()=>{
  const classes = useStyles();
  const [value, setValue] = React.useState(0);
  const [loader, showLoader]                  = useState(false);
  const [errorMessage, setErrorMessage]       = useState("");
  const [showError, setShowError]             = useState(false);
  const [threadCount, setThreadCount]         = useState(
        localStorage.getItem(Utils.LS_KEY_THREAD_COUNT)!=null?
          localStorage.getItem(Utils.LS_KEY_THREAD_COUNT):25);
  const [showSuccess, setShowSuccess]         = useState(false);
  const [successMessage, setSuccessMessage]   = useState("");
  const [modal, showModal] = useState(false);
  const [content, setContent] = useState(null);

  
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
    setTimeout(function(){ closeErrorAlert() }, 5000);
 } 

//  const setThreadChangeHandler=(thread)=>{
//     setThreadCount(thread)
//  }

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };


  const viewConfig = () => {
    APIService.callAPIGet(Utils.API_URL + Utils.API_CONFIG_PATH)
      .then(data => {
        showModal(true)
        setContent(data)
      }).catch(error => {
        console.log("error" + error);
        showLoader(false);
        setError(error.message)
      });
  }


  return (
    <div className={classes.root}>
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
              className="close"
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
        <Paper square>
        <AppBar position="static" color="transparent">
        <Tabs value={value}
         onChange={handleChange} 
         variant="fullWidth" 
         indicatorColor="primary"
         textColor="primary"
         centered
          aria-label="simple tabs example">
          <Tab label="Workflows" {...a11yProps(0)} />
          <Tab label="Configuration" {...a11yProps(2)} />
        </Tabs>
        </AppBar>
        <button onClick={viewConfig} id="viewConfigButton" className="view-config">View Config</button>
        <GWDialog title={"Server Configurartion"} content={content} onClose={() => { showModal(false); setContent(null) }} show={modal} />
      <TabPanel value={value} index={0}>
      <Processing  setError={setError}   showLoader = {showLoader} showSuccessAlert={showSuccessAlert} threadCount={threadCount} />
      <Dashboard/>
      </TabPanel>
      <TabPanel value={value} index={1}>
      <Configuration setError={setError}   showLoader = {showLoader}  showSuccessAlert={showSuccessAlert} threadCount={threadCount}  setThreadCount ={setThreadCount}/>
      </TabPanel>
      </Paper>
     
    
    </div>
  );
}


ReactDOM.render(
  React.createElement(Workflows, null),
  document.getElementById("react")
)
