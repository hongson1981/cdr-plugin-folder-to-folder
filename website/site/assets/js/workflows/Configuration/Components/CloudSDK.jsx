import React, { useState }      from "react";
import GWButton                 from "../../../components/buttons/GWButton";
import EditableTable                 from "../../../components/EditableTable/EditableTable";
import * as APIService          from "../../../services/Services";
import * as Utils               from "../../../services/Utils";
import swal                     from 'sweetalert';
import ReactJson                from 'react-json-view'

export default function CloudSDK(props) {
    const [liveIPList, setLiveIpList] = useState([]);
    const [updatedIPList, setUpdatedIPList] = React.useState( localStorage.getItem(Utils.LS_KEY_SDK_IP) ? JSON.parse(localStorage.getItem(Utils.LS_KEY_SDK_IP)):[] )
    //const [updatedIPList, setUpdatedIPList] = React.useState( [] )
    const [skipPageReset, setSkipPageReset] = React.useState(false)
    const [refresh, setRefresh] = React.useState(true)

    const columns = React.useMemo(
        () => [
          {
            Header: 'SDK IP',
            columns: [
              {
                Header: 'IP',
                accessor: 'IP',
              },
              {
                Header: 'Port',
                accessor: 'Port',
              },
            ],
          }
        ]
      )

    const updateMyData = (rowIndex, columnId, value) => {
        // We also turn on the flag to not reset the page
        setSkipPageReset(true)
        setUpdatedIPList(old =>
          old.map((row, index) => {
            if (index === rowIndex) {
              return {
                ...old[rowIndex],
                [columnId]: value,
              }
            }
            return row
          })
        )
        localStorage.setItem(Utils.LS_KEY_SDK_IP, JSON.stringify(updatedIPList));
      }
    
      // After data chagnes, we turn the flag back off
      // so that if data actually changes when we're not
      // editing it, the page is reset
      React.useEffect(() => {
        setSkipPageReset(true)
      }, [updatedIPList])
    
      // Let's add a data resetter/randomizer to help
      // illustrate that flow...
      const resetData = () => {
          setUpdatedIPList([]);
          setRefresh(!refresh);
          localStorage.setItem(Utils.LS_KEY_SDK_IP, []);
      }


    const addKeys = (liveIps, port) => {
        var sdkIps = []
        liveIps.map(item => {
            let obj = { IP: item, Port: port }
            sdkIps.push(obj)
        })
        setLiveIpList(sdkIps)
        setUpdatedIPList(JSON.parse(JSON.stringify(sdkIps)));
        localStorage.setItem(Utils.LS_KEY_SDK_IP, JSON.stringify(sdkIps));
    }

    const showLoader = (show) => {
        props.showLoader(show);
    }

    const loadLiveIPs = (alert = false) => {
        props.showLoader(true);
        APIService.callAPIGet(Utils.SDK_SERVER_IPS + Utils.LOAD_CLOUD_SDK_IPS)
            .then(data => {
                addKeys(data.live_ips, "8080");
                showLoader(false);
            }).catch(error => {
                console.log("error" + error);
                props.setError(error.message)
                showLoader(false);
            });
    }

    const setPlugInCallback = () => {
        if (updatedIPList.length == 0) {
            swal("Set Plugin IPs failed", "IP list is empty", "error");
            return;
        }
        showLoader(true);
        APIService.callAPIPost(Utils.API_URL + Utils.SET_PLUGIN_IPS,
            { "Endpoints": updatedIPList })
            .then(data => {
                if (data.Endpoints) {
                    props.showSuccessAlert("Successfully set");
                    setUpdatedIPList(data.Endpoints)
                } else {
                    props.setError(data.detail)
                    loadLiveIPs();
                }
                showLoader(false);

            }).catch(error => {
                showLoader(false);
                props.setError(error.message)
              
            });

    }

    const addData =()=>{
        var record = {IP:'0.0.0.0', Port:"8080"}
        var existing = updatedIPList;

        existing.push(record);
        setUpdatedIPList(existing)
        setRefresh(!refresh);
        localStorage.setItem(Utils.LS_KEY_SDK_IP, JSON.stringify(existing));

    }

    return (
        <div>
            <div className="card-holder">
                <div className="cdr-left">
                    {/* <ReactJson src={updatedLiveIps}
                        theme="twilight"
                        onEdit={true}
                        onAdd={true}
                        onDelete={true}
                        name="SDK"
                        onEdit={e => {
                            console.log(e)
                            if (e.new_value == "error") {
                                return false
                            }
                            setUpdatedLiveIps(e.updated_src);
                        }}
                        displayDataTypes={false} /> */}
                    {/* <button onClick={resetData}></button> */}
                    <div className="sdk-btn-grp">
                        <GWButton showLoader={false} text="Reset" callback={resetData} classname="clear-data" />
                        <GWButton showLoader={false} text="Add" callback={addData} classname="start-processing" />
                    </div>
                    <EditableTable
                        columns={columns}
                        data={updatedIPList}
                        updateMyData={updateMyData}
                        skipPageReset={skipPageReset}
                    />
                </div>
                <div className="buttons-group sdk-buttons">
                    <GWButton showLoader={false} text={"Load from AWS"} callback={loadLiveIPs} classname="start-processing" />
                    <div className="setPluginIps">
                        <GWButton showLoader={false} text="Set Plugin IPs" callback={setPlugInCallback} classname="stop-processing" />

                    </div>
                </div>
            </div>

        </div>
    );
}




