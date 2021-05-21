import * as React from "react";
import * as ReactDOM from "react-dom";
import  HighlightTexts  from './HighlightTexts';

const App =()=>{
    return(
        <>
        <HighlightTexts/>
       </> 
    )
}


ReactDOM.render(
    React.createElement(App , null),
    document.getElementById("react")
)