import React, { Fragment, useState, useEffect, useCallback, styl } from 'react'
import SideBar from 'components/SideBar'

const Page = ({ history }) => {

    return (
        <div className="padding-top-30 padding-bottom-30">
            <div className="row padding-bottom-100">
                <div className="large-10 push-2 columns">
                    <div id="redeem">
                        <form id="redeem_form" novalidate="novalidate" ng-submit="processForm()">
                            <div className="row">
                                <div className="large-8 columns">
                                    <h5>Redeem Code</h5>
                                    <p>
                                        <label for="redeem_code">Redeem code:</label>
                                        <input type="text" name="redeem_code" id="redeem_code" tabindex="2" placeholder="Redeem Code" ng-model="redeem_code" required />
                                    </p>
                                    <p>
                                        <label for="code_type">Code type:</label>
                                        <select type="text" name="code_type" id="code_type" tabindex="3" ng-model="code_type.value" ng-options="v.name for v in code_type.values track by v.id" required>
                                            <option value="">- Choose Code Type -</option>
                                        </select>
                                    </p>
                                    <button type="submit" className="button expand">Submit</button>
                                    <div className="loader">
                                        <img id="loading-image" src="/static/assets/frontend/images/ajax-spinner.gif" alt="Loading..." />
                                    </div>
                                </div>
                            </div>
                        </form>
                    </div>
                </div>

                <SideBar />
            </div>
        </div>
    )
}

export default Page