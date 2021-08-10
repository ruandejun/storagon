import React from "react"
import { connect } from 'react-redux'
import { makeStyles } from '@material-ui/core/styles'
import TopBarButtonGroups from './TopBarButtonGroups'
import { Grid, Radio, Divider, FormControlLabel } from '@material-ui/core/'
import Menu from '@material-ui/core/Menu'
import MenuItem from '@material-ui/core/MenuItem'


const useStyles = makeStyles(theme => ({
    root: {
      flexGrow: 1,
    },
    paper: {
      padding: theme.spacing(2),
      textAlign: 'center',
      color: theme.palette.text.secondary,
    },
    container: {
        padding: '5px',
        borderBottom: '1px solid #868DAA',
        background: "#f6f7fd"
    },
    menuItem:{
        padding:'0px',
        fontSize: '13px',
        width: '250px',
        display:'block',
        '& span':{
            fontSize: '13px'
        },
        '& label':{
            margin:'0px'
        },
        '& svg':{
            width: '15px'
        }
    }
}));


const Page = (props) => {
    const classes = useStyles();
    const { buttons} = props;
    const [anchorEl, setAnchorEl] = React.useState(null);
    const [open, setOpen] = React.useState({sorting:false,search:false,settings:false});
    const orderFiles = {
        orderBy: 'asc',
        field: 'name'
    }
    const showImages = 'thumbs'

    const handleOpenMenu = (event, name) => {
        switch (name) {
            case 'sorting':
                setOpen({sorting: true})
                break;
            case 'search':
                setOpen({search: true})
                break;
            case 'settings':
                setOpen({settings: true})
                break;
        
            default:
                break;
        }
        setAnchorEl(event.currentTarget);
    };

    const handleSetOrderBy = (orderBy) =>{
        // props.setSorting(orderBy, orderFiles.field);
        // props.filterSorting();
    }

    const handleSetOrderField = (field) =>{
        // props.setSorting(orderFiles.orderBy, field);
        // props.filterSorting();
    }

    const handleClose = () => {
        setAnchorEl(null);
        setOpen({sorting:false,search:false,settings:false});
    };

    const handleSetSettings = (imagePreview) =>{
        // props.setImagesSettings(imagePreview);
    }


    const options = [
        {
            name: 'By Name',
            value:'name'
        },
        {
            name: 'By Size',
            value:'size'
        },
        {
            name: 'By Create Date',
            value:'date'
        }
    ];

    const additionalButtons = [
        {
            title: 'Sorting',
            icon: 'sort',
            onClick: (e)=> handleOpenMenu(e,'sorting'),
            disable: false
        },
        {
            title: 'Settings',
            icon: 'cog',
            onClick: (e)=> handleOpenMenu(e,'settings'),
            disable: false
        }
    ]

    return (
        <>
            <Grid container className={classes.container} >
                {buttons.topbar.map((groups, index)=> 
                    <Grid item key={index}>
                        <TopBarButtonGroups buttons={groups} index={index} />
                    </Grid>
                )}
            
                <Grid style={{ marginLeft: "auto" }}>
                    <TopBarButtonGroups buttons={additionalButtons} />
                        <Menu
                            id="sorting-menu"
                            anchorEl={anchorEl}
                            keepMounted
                            open={Boolean(open.sorting)}
                            onClose={handleClose}
                        >
                            {options.map((option,index) => (
                                <MenuItem key={index} className={classes.menuItem} selected={option.value === orderFiles.field}>
                                        <FormControlLabel value={option.value} control={
                                            <Radio name='orderField' checked={option.value === orderFiles.field} onChange={()=>handleSetOrderField(option.value)} value={option.value} />
                                        } label={option.name}  />
                                </MenuItem>
                            ))}
                            <Divider />
                            <MenuItem className={classes.menuItem} selected={'asc' === orderFiles.orderBy}>
                                <FormControlLabel control={<Radio name='orderby' checked={'asc' === orderFiles.orderBy} onChange={()=>handleSetOrderBy('asc')} value='asc' />} label='Ascending'  />
                            </MenuItem>
                            <MenuItem className={classes.menuItem} selected={'desc' === orderFiles.orderBy}>
                                <FormControlLabel control={<Radio name='orderby' checked={'desc' === orderFiles.orderBy} onChange={()=>handleSetOrderBy('desc')} value='desc' />} label='Descending'  />
                            </MenuItem>
                        </Menu>


                        <Menu
                            id="settings-menu"
                            anchorEl={anchorEl}
                            keepMounted
                            open={Boolean(open.settings)}
                            onClose={handleClose}
                        >
                            <MenuItem className={classes.menuItem} selected={showImages === 'thumbs'}>
                                <FormControlLabel control={
                                    <Radio name='imageSettings' checked={showImages === 'thumbs'} onChange={()=>{handleSetSettings('thumbs')}} value='thumbs' />
                                } label='Show Thumbs'  />
                            </MenuItem>
                            <MenuItem className={classes.menuItem} selected={showImages === 'icons'}>
                                <FormControlLabel control={
                                    <Radio name='imageSettings' checked={showImages === 'icons'} onChange={()=>{handleSetSettings('icons')}} value='icons' />
                                } label='Show Icons'  />
                            </MenuItem>
                        </Menu>

                </Grid>

            </Grid>

        </>
    )
}

export default Page