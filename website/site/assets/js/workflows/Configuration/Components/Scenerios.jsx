import React, { useState }      from "react";
import * as APIService          from "../../../services/Services";
import * as Utils               from "../../../services/Utils";
import { withStyles }           from '@material-ui/core/styles';
import { green }                from '@material-ui/core/colors';
import Radio                    from '@material-ui/core/Radio';
import RadioGroup               from '@material-ui/core/RadioGroup';
import FormControlLabel         from '@material-ui/core/FormControlLabel';
import FormControl              from '@material-ui/core/FormControl';
import FormLabel                from '@material-ui/core/FormLabel';

export default function Scenarios(props) {

  const [defaultVolume, setDefaultVolume] = useState(localStorage.getItem(Utils.LS_KEY_BASEDIR));
  const [type, setType]                   = useState(localStorage.getItem(Utils.LS_KEY_VOLUME_TYPE)||Utils.VOLUME_DEFAULT);
  const [hd1, setHD1]                     = useState(localStorage.getItem(Utils.VOLUME_HD1, ""))
  const [hd2, setHD2]                     = useState(localStorage.getItem(Utils.VOLUME_HD2, ""))
  const [hd3, setHD3]                     = useState(localStorage.getItem(Utils.VOLUME_HD3, ""))
  const [customVolume, setCustomVolume]   = useState({hd1:"test",hd2:"test2", hd3:"test3"})
  const [scenarios, setScenarios]         = useState(null)


  React.useEffect(() => {
   loadScenarios();
}, []);


const loadScenarios = (alert = false) => {
  props.showLoader(true);
  APIService.callAPIGet(Utils.API_URL + Utils.API_CONFIGURE_SCENARIOS)
      .then(data => {
          setScenarios(data)
          showLoader(false);
      }).catch(error => {
          console.log("error" + error);
          props.setError(error.message)
          showLoader(false);
      });
}
  const showLoader = (show) => {
    props.showLoader(show);
  }

  const saveVolumes = () => {
    if(type === Utils.VOLUME_DEFAULT){
      if(scenarios){
        var sel = document.getElementById('baseDirSelect');
        bodyFormat = {
          "hd1_path": "./test_data/" + sel.value + "/hd1",
          "hd2_path": "./test_data/" + sel.value + "/hd2",
          "hd3_path": "./test_data/" + sel.value + "/hd3"
        }
        localStorage.setItem(Utils.LS_KEY_BASEDIR, sel.value);
        setDefaultVolume(sel.value);
      }else{
        props.setError("No scenario available")
        return;
      }
    }else if(type === Utils.VOLUME_CUSTOM){
      bodyFormat = {
        "hd1_path": hd1,
        "hd2_path": hd2,
        "hd3_path": hd3,
      }
    }

    showLoader(true);
    APIService.callAPIPost(Utils.API_URL + Utils.API_CONFIGURE_ENV, bodyFormat)
      .then(data => {
        showLoader(false);
        if(!data.detail){
          props.showSuccessAlert("Successfully Configured")
        }else{
          props.setError(data.detail)
        }
        
      }).catch(error => {
        console.log("error" + error);
        showLoader(false);
        props.setError(error.message)
      });
  }


  const updateDefaultVolume = (element) => {
    setDefaultVolume(element.target.value)
  }


  const handleCustomVolume =(event)=>{
    event.preventDefault();
    var dir = customVolume;
    dir[event.target.name] = event.target.value;
    setCustomVolume(dir);
    
    if(event.target.id === "hd1"){
      setHD1(event.target.value)
      localStorage.setItem(Utils.VOLUME_HD1, event.target.value)
    }else if(event.target.id === "hd2"){
      setHD2(event.target.value)
      localStorage.setItem(Utils.VOLUME_HD2, event.target.value)
    }else if(event.target.id === "hd3"){
      setHD3(event.target.value)
      localStorage.setItem(Utils.VOLUME_HD3, event.target.value)
    }
    event.stopPropagation();
  }

 
  const handleChange = (event) => {
    setType(event.target.value);
    localStorage.setItem(Utils.LS_KEY_VOLUME_TYPE, event.target.value)
  };

  return (
    <div>
      <div className="card-holder">
        <FormLabel component="legend">Select rebuild volume location</FormLabel>
          <FormControl component="fieldset">
            <RadioGroup row aria-label="position" name="position" defaultValue={type} onChange={handleChange}>
              <FormControlLabel name="basedir" value="default" checked = {type == "default"} control={<Radio color="primary" />} label="Scenarios" />
              <FormControlLabel name="basedir"  value="custom" checked = {type == "custom"} control={<Radio color="primary" />} label="Custom" />
            </RadioGroup>
          </FormControl>
        <div className="cdr-left cdr-second">
          <div className="middle-cdr">
            {type == "default" &&
              <div className="middle-cdr-cont">
                <div className="dropboxdiv">
                  <select
                    type="text"
                    placeholder=""
                    id="baseDirSelect"
                    className="form-control dropbox_scenario"
                    value={defaultVolume}
                    onChange={updateDefaultVolume}
                  >
                    {
                      scenarios && scenarios.map((folder, index) => {
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
            }
             { type == "custom" &&
                 
                <div className="threads-count">
                  <div className="middle-cdr mg-b-10">
                
                      <label>HD 1</label>
                      <input
                        type="text"
                        placeholder="scenario 1"
                        id="hd1"
                        value={hd1}
                        className="form-control"
                        onChange={handleCustomVolume}
                      />
                      <label>HD 2</label>
                      <input
                        type="text"
                        placeholder="scenario 2"
                        id="hd2"
                        value={hd2}
                        className="form-control"
                        onChange={handleCustomVolume}
                      />
                      <label>HD 3</label>
                      <input
                        type="text"
                        placeholder="scenario 3"
                        id="hd3"
                        value={hd3}
                        className="form-control"
                        onChange={handleCustomVolume}
                      />
                    </div>
                  </div>
          }
          </div>
        </div>
        <div className="clear"></div>
        <button className="set-base-dir-btn" onClick={saveVolumes} >Set base dir</button>
      </div>
    </div>
  );
}




