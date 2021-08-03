import React, { Fragment, useState, useEffect, useCallback, styl } from 'react'
import SideBar from 'components/SideBar'

const Page = ({ history }) => {

    return (
        <div className="padding-top-30 padding-bottom-30">
            <div className="row padding-bottom-100">
                <div className="large-10 push-2 columns">
                    <h5>Your current point: pointBalance </h5>
                    <div className="row">
                        <div ng-repeat="pack in packs" className="small-12 large-3 medium-3 columns">
                            <div className="panel callout radius">
                                <ul style={{listStyle: 'none', textAlign: 'center'}}>
                                    <li style={{padding: 5}}>pack.name</li>
                                    <li style={{padding: 5}}>pack.value</li>
                                    <a href="" className="tiny button success radius" ng-click="exchange(pack.name)">Exchange</a>
                                </ul>
                            </div>
                        </div>
                    </div>
                </div>

                <SideBar />
            </div>
        </div>
    )
}

export default Page