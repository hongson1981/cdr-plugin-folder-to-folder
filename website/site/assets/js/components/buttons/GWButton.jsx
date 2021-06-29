import React, {useState} from "react";
import Loader             from  "../Loader/Loader";

export default function GWButton (props) {
   return(
      <>
      <div className="btn-loader-container">
      <button 
         onClick={props.callback}
         className={props.classname}>
            {props.text}
      </button>
      {props.showLoader && <Loader></Loader>}
      </div>
      </>
   );
}
