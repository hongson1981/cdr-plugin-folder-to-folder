import React, { useState } from "react";
import * as Utils from "../../../services/Utils";



export default function ThreadCount(props) {

  const [threadCount, setThreadCount] = useState(props.threadCount);

  const onThreadChange = (event) => {
    setThreadCount(event.target.value);
    props.setThreadCount(event.target.value);
    localStorage.setItem(Utils.LS_KEY_THREAD_COUNT, event.target.value);
  }

  return (
    <div>
      <div className="card-holder">
        <div className="cdr-left cdr-second">
          <div className="middle-cdr">
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




