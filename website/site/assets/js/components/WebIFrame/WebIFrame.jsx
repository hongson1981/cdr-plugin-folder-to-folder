import * as React               from 'react';
import Iframe                   from 'react-iframe'


const WebIFrame= props =>{
    return(           
        <div>
         <Iframe
                url= {props.url}
                width="100%"
                height="600"
                style="display:block; border:none; height:100vh; width:100%;"
            ></Iframe>    
             <hr/>
                Site loaded above: <a href={props.url} target="_blank">{props.url}</a>                                                        
        </div>
        
    )
}

export default WebIFrame;