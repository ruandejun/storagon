import React from 'react'

const Page = () => {

    return (
        <div>
            <div class="container">
                <div class="text-center">
                    <h3>File Information</h3>
                    <p>Name: <strong>{file_name}</strong></p>
                    <p>Size: <strong>{file_size}</strong></p>

                </div>
                <div class="col-sm-12 col-md-8 col-md-offset-2">
                    <table class="table table-hover table-bordered" style="display:none;">
                        <thead>
                            <tr>
                                <th>FEATURES</th>
                                <th>FREE</th>
                                <th>PREMIUM</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <th>Storage Space</th>
                                <th>50 GB</th>
                                <th>500 GB and more</th>
                            </tr>
                            <tr>
                                <th>Monthly Bandwidth</th>
                                <th>250 GB</th>
                                <th>1 TB and more</th>
                            </tr>
                            <tr>
                                <th>Download Speed</th>
                                <th>Average</th>
                                <th>Unlimited</th>
                            </tr>
                            <tr>
                                <th>Download Wait</th>
                                <th>30 seconds</th>
                                <th>No wait</th>
                            </tr>
                            <tr>
                                <th>Access to Premium files</th>
                                <th><span class="glyphicon glyphicon-remove"></span></th>
                                <th><span class="glyphicon glyphicon-ok"></span></th>
                            </tr>
                            <tr>
                                <th>Access to Premium tools</th>
                                <th><span class="glyphicon glyphicon-remove"></span></th>
                                <th><span class="glyphicon glyphicon-ok"></span></th>
                            </tr>
                            <tr>
                                <th>Limit number of download per day</th>
                                <th><span class="glyphicon glyphicon-ok"></span></th>
                                <th><span class="glyphicon glyphicon-remove"></span></th>
                            </tr>
                            <tr>
                                <th>24/7 Customer Support</th>
                                <th><span class="glyphicon glyphicon-remove"></span></th>
                                <th><span class="glyphicon glyphicon-ok"></span></th>
                            </tr>
                            <tr>
                                <th>Automatic Delete File</th>
                                <th>Never</th>
                                <th>Never</th>
                            </tr>
                            <tr>
                                <th>Pricing</th>
                                <th>Free</th>
                                <th><h3>$12.99 /mo</h3></th>
                            </tr>
                            <tr>
                                <th>Spped</th>
                                <th>Slow</th>
                                <th>Fast</th>
                            </tr>
                            <tr>
                                <th>&nbsp</th>
                                <th>
                                    <a href="javascript:void(0)" id="showFreeDownloadProcess" class="btn btn-danger">Slow Download</a>

                                </th>
                                <th>
                                    <a href="javascript:void(0)" id="showPlanModal" class="btn btn-danger">Fast Download</a>
                                </th>
                            </tr>
                        </tbody>
                    </table>
                </div>
                <div class="vertical-padding-top"></div>
                <div class="col-sm-12 col-md-8 col-md-offset-2" id="downloadProcess" style="display:none;">
                    <div class="row text-center countdown">
                        <h1>
                            <span class="hours">00</span>:
                            <span class="minutes">00</span>:
                            <span class="seconds">00</span>
                        </h1>
                        <div id="progress"></div>
                    </div>
                    <div class="text-center">
                        <a id="result_file" class="text-center" href="javascript:void(0)" download="{{file_name}}"></a>
                    </div>
                    <div id="help_message_download" class="row text-center">
                        <h3>Please choose your download type</h3>
                    </div>
                    <div class="vertical-padding-top"></div>
                    <div class="text-center">
                        <a class="btn btn-success" id="freedl" title="Download and decrypt file using browser">Download</a>
                        <a class="btn btn-primary" id="torrentdl" title="Download encrypted file with torrent">Download torrent</a>
                    </div>
                    <input type="hidden" id="user_id" value={user.profile.id} />
                    <div class="vertical-padding-top"></div>
                </div>
            </div>
        </div>
    )
}

export default Page