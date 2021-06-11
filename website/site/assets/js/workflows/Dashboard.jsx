

import React, {useState}    from "react";
import WebIFrame            from  "../components/WebIFrame/WebIFrame";
import * as Utils          from "../services/Utils";

export default function Dashboard(props) {

  const [random, setRandom]     = useState(0);


  const resetIframe=()=>{
    setRandom(random+1);
  }

   return(
      <>

    <div className="card-holder">
    <button  onClick={() => { resetIframe(); }} id="refreshIframe" className="refresh-iframe">Refresh</button>
        <div className="iframe-container">
            <WebIFrame url ={Utils.DASHBOARD_URL} />
        </div>
    </div>

      </>
   );
}
