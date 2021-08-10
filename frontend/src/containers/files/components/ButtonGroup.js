import React from 'react'
import Icon from '@material-ui/core/Icon'
import Button from '@material-ui/core/Button'
import ButtonGroup from '@material-ui/core/ButtonGroup'
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome'

export default function InputField(props) {
        const { buttons} = props;

        const buttonsComponents = buttons.map((button, i) => (
            <Button
                className={`customIconButton ${button.class}`}
                key={i}
                variant={button.varinat || 'contained'}
                color={button.color || 'primary'}
                size={button.size}
                startIcon={<FontAwesomeIcon icon={button.icon} />}
                onClick={() => button.onClick() }
            >
                {button.label}
            </Button>
        ));
        return (
            <ButtonGroup variant="text" color="primary" >
                {buttonsComponents}          
            </ButtonGroup>
        );
}
