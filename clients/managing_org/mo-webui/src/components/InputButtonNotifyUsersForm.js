import React from 'react';
import {makeStyles} from '@material-ui/core/styles';
import {Button, Grid, TextField} from "@material-ui/core";
import {MO_SERVER_HOST, MO_SERVER_PORT} from "../services/ConfigService";

const axios = require('axios').default;

export class InputButtonNotifyUsersForm extends React.Component {
    constructor(props) {
        super(props);
        this.state = {value: ''};
        this.handleChange = this.handleChange.bind(this);
        this.handleSubmit = this.handleSubmit.bind(this);
    }

    handleChange(event) {
        this.setState({value: event.target.value});
    }

    handleSubmit(event) {
        alert('Notify all users to send data for query: ' + this.state.value);
        event.preventDefault();

        try {
            return axios.post(`http://${MO_SERVER_HOST}:${MO_SERVER_PORT}/sendData/` + this.state.value);
        } catch (error) {
            console.error(error);
        }


    }

    render() {
        return (
            <form onSubmit={this.handleSubmit}>
                <Grid container direction="row"
                      justify="center"
                      alignItems="center"
                      spacing={1}>
                    <Grid item>
                        <TextField id="outlined-basic" label={this.props.fieldText} variant="outlined"
                                   value={this.state.value} onChange={this.handleChange}/>
                    </Grid>
                    <Grid item>
                        <Button type="submit" variant="contained" color="secondary">
                            {this.props.buttonText}
                        </Button>
                    </Grid>
                </Grid>
            </form>
        );
    }
}