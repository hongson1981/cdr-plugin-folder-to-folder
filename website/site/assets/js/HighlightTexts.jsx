import * as React     from "react";
import * as ReactDOM from "react-dom";
import      ReactJson from 'react-json-view'
import * as params    from '@params';//to load any variable passed from template to your JS files

const HighlightTexts= ()=>{
    
    const [configuration, setConfiguration] = React.useState({});

    React.useEffect(() => {
      fetch(params.url)
      .then(res => res.json())
      .then((data) => {
          console.log(JSON.stringify(data))
          setConfiguration((data))
      })
      .catch(console.log)
  }, []);
   
    return(

      <div >
         <ReactJson src={configuration}
                    theme="monokai"
                    onEdit ={true}
                    onDelete={true}
                    name="Config"
                    displayDataTypes={false}/>
      </div>
    )
}


ReactDOM.render(
  React.createElement(HighlightTexts , null),
  document.getElementById("react")
)