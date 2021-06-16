import * as React     from "react";
import * as ReactDOM from "react-dom";
import      ReactJson from 'react-json-view'
import * as params    from '@params';//to load any variable passed from template to your JS files
import Workflow from './workflows/Workflow'

const Workflows= ()=>{
    
    const [configuration, setConfiguration] = React.useState({});

   
    return(

      <div >
	    <Workflow/>
                    
      </div>
    )
}


ReactDOM.render(
  React.createElement(Workflows, null),
  document.getElementById("react")
)
