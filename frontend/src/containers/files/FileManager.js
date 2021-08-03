import React from 'react'
import { FileManager, FileNavigator } from '@opuscapita/react-filemanager'
import connectorNodeV1 from '@opuscapita/react-filemanager-connector-node-v1'

const apiOptions = {
    ...connectorNodeV1.apiOptions,
    apiRoot: `http://opuscapita-filemanager-demo-master.azurewebsites.net/` // Or you local Server Node V1 installation.
}

const Page = ({ history }) => {

    return (
        <div >
            <div
                style={{
                    height: '70vh',
                    minWidth: '320px',
                    flex: '1',
                    padding: '12px',
                    backgroundColor: '#f5f5f5'
                }}>
                <FileManager>
                    <FileNavigator
                        id="filemanager-1"
                        api={connectorNodeV1.api}
                        apiOptions={apiOptions}
                        capabilities={connectorNodeV1.capabilities}
                        listViewLayout={connectorNodeV1.listViewLayout}
                        viewLayoutOptions={connectorNodeV1.viewLayoutOptions}
                    />
                </FileManager>
            </div>

        </div>
    )
}

export default Page