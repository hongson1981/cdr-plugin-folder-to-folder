import * as React     from "react";
import      ReactJson from 'react-json-view'


const HighlightTexts= ()=>{
    
    const [Ips, setIPs] = React.useState("");

    React.useEffect(() => {
      fetch('http://localhost:8880/configuration/config/')
      .then(res => res.json())
      .then((data) => {
          console.log(JSON.stringify(data))
          setIPs((data))
      })
      .catch(console.log)
  }, []);
   
    return(

      <div >
         <ReactJson src={Ips && Ips}
                    theme="monokai"
                    onEdit ={true}
                    onDelete={true}
                    name="Config"
                    displayDataTypes={false}/>
      </div>
    )
}
export default HighlightTexts 