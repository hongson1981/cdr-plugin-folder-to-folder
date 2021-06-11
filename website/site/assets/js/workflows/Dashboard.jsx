

import React, {useState}    from "react";
import WebIFrame            from  "../components/WebIFrame/WebIFrame";
import * as Utils          from "../services/Utils";

export default function Dashboard(props) {

  const [update, setUpdate]     = useState(false);

  refreshHandler=()=>{
    setUpdate(!update);
  }
   return(
      <>

    <div className="card-holder">
    {/* <button id="refreshIframe" className="refresh-iframe">Refresh</button> */}
        <div className="iframe-container">
            <WebIFrame url ={Utils.DASHBOARD_URL} />
        </div>
    </div>

      </>
   );
}
