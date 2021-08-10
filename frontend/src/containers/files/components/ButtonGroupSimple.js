import React from 'react'
import Button from '@material-ui/core/Button'
import ButtonGroup from '@material-ui/core/ButtonGroup'
import { makeStyles } from '@material-ui/core/styles'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'

const useStyles = makeStyles(theme => ({
  root: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    '& > *': {
      margin: theme.spacing(1),
    },
  },
  iconStyle: {
      paddingRight: '10px'
  },
  button: {
      fontSize:'12px'
  }
}));

export default function ButtonGroupSimple(props){
  const classes = useStyles();
  const { buttons, index } = props;
  console.log({buttons})
  return (
    <div className={classes.root}>
      <ButtonGroup key={index} color="primary" aria-label="outlined primary button group">
        {buttons.map((button, index)=>{
            return <Button key={index} className={classes.button} onClick={button.onClick} disabled={Boolean(button.disabled)}>
                        {button.icon && <FontAwesomeIcon icon={button.icon} style={{marginRight: 5}}/>}{button.label}
                    </Button>
        })}
      </ButtonGroup>
    </div>
  );
}
