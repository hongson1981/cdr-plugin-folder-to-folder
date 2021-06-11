import * as React       from "react";
import * as ReactDOM    from "react-dom";
import Workflow         from "./Workflow";


const App =()=>{
    return(
        <>
        <Workflow/>
       </> 
    )
}

ReactDOM.render(
    React.createElement(App , null),
    document.getElementById("react")
)