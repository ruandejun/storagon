import React, {useEffect} from 'react'
import SideBar from 'components/SideBar'
import actions from './redux/action'
import {useDispatch, useSelector} from 'react-redux'

const { getExchange, getBalance } = actions

const Page = ({ }) => {
    const dispatch = useDispatch()
    const userExchange = useSelector((state) => state.account.exchange)
    const userBalance = useSelector((state) => state.account.balance)

    useEffect(() => {
        dispatch(getBalance())
        dispatch(getExchange())

        return () => { }
    }, [])

    const pointBalance = userBalance ? userBalance[1].fields.amount : 0
    const packs = userExchange ? userExchange.packs : []

    const exchange = (name) => {

    }

    return (
        <div className="padding-top-30 padding-bottom-30">
            <div className="row padding-bottom-100">
                <div className="large-10 push-2 columns">
                    <h5>Your current point: {pointBalance} </h5>
                    <div className="row">
                        {packs.map((pack) => {
                            return (
                                <div className="small-12 large-3 medium-3 columns">
                                    <div className="panel callout radius">
                                        <ul style={{ listStyle: 'none', textAlign: 'center' }}>
                                            <li style={{ padding: 5 }}>{pack.name}</li>
                                            <li style={{ padding: 5 }}>{pack.value}</li>
                                            <a href="" className="tiny button success radius" onClick={exchange(pack.name)}>Exchange</a>
                                        </ul>
                                    </div>
                                </div>
                            )
                        })}
                    </div>
                </div>

                <SideBar />
            </div>
        </div>
    )
}

export default Page