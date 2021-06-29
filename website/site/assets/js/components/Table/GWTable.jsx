import React, {useState} from "react";

export default function GWTable (props)  {

   const renderTableHeader= () =>{
       console.log("props.data" + JSON.stringify(props.data));
       let header = Object.keys(props.data[0])
       return header.map((key, index) => {
          return <th key={index}>{key.toUpperCase()}</th>
       })
    }
 
   const  renderTableData =() => {
       return props.data.map((item, index) => {
          const { ip, port} = item //destructuring
          return (
             <tr key={ip}>
                <td>{ip}</td>
                <td>{port}</td>
             </tr>
          )
       })
    }
 
    return (
        <div>
            {/* <h1 id='title'>React Dynamic Table</h1> */}
            <table id='gw-table'>
            <tbody>
                <tr>{renderTableHeader()}</tr>
                {renderTableData()}
            </tbody>
            </table>
        </div>
    );
    
 }
 
