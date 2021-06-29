import React, { useState }  from "react";
import      ReactJson       from 'react-json-view'


const GWDialog= props =>{
    
    
    
   if(!props.show){
       return null
   }

    return(           
        <div className="modal" onClick={props.onClose}>  
         <div className="modal-content" onClick={e => e.stopPropagation()}>
             <div className="modal-header">
                 <h4 className="modal-title">{props.title}</h4>
                 <button onClick={props.onClose} className="button">&times;</button>
             </div>
             <div className="modal-body">
                 {/* {JSON.stringify(jsonData)} */}
                 <ReactJson src={props.content}
                    theme="monokai"
                    onEdit ={true}
                    onDelete={true}
                    name={false}
                    displayDataTypes={false}/>
             </div>
            
         </div>
        </div>
    )
}

export default GWDialog;