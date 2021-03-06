import React, {useState} from "react";
import {makeStyles} from '@material-ui/core/styles';

import {AppBar, Toolbar, Button, IconButton, Typography, TextField} from "@material-ui/core";
import {Grid, Paper} from "@material-ui/core";
import GroupIcon from '@material-ui/icons/Group';

import RequestsTable from "../components/RequestsTable";
import {InputButtonApproveQuery} from "../components/InputButtonApproveQuery";
import RequestsQuery from "../components/RequestsQuery";
import GavelIcon from '@material-ui/icons/Gavel';

const useStyles = makeStyles((theme) => ({
    root: {
        flexGrow: 1,
    },
    menuButton: {
        marginRight: theme.spacing(2),
    },
    title: {
        flexGrow: 1,
    },
    icon: {
        marginRight: theme.spacing(1)
    },
    content: {
        padding: theme.spacing(2)
    },
    paper: {
        padding: theme.spacing(2),
        textAlign: 'center',
        color: theme.palette.text.secondary,
    },
    demo: {
        backgroundColor: theme.palette.background.default,
    }
}));

export default function LandingView(props) {
    const classes = useStyles();

    return (
        <div className={classes.root}>
            <AppBar position="static">
                <Grid container
                      direction="row"
                      justify="center"
                      alignItems="center">
                    <Grid item>
                        <Toolbar>
                            <Grid item>
                                <GavelIcon className={classes.icon}/>
                            </Grid>
                            <Grid item>
                                <Typography variant="h6" className={classes.title}>
                                    Oversight Organization
                                </Typography>
                            </Grid>
                        </Toolbar>
                    </Grid>
                </Grid>
            </AppBar>

            <Grid container spacing={3} className={classes.content}>
                <Grid item xs={12}>
                </Grid>
                <Grid item xs={12} sm={6}>
                    <RequestsTable/>
                </Grid>
                <Grid container sm={6} spacing={3}
                      direction="row"
                      justify="center"
                      alignItems="center">
                    <Grid item s>
                        <InputButtonApproveQuery buttonText="Approve Query" fieldText="Query ID"/>
                    </Grid>
                </Grid>
                <Grid item xs={12}>
                    <RequestsQuery/>
                </Grid>
            </Grid>
        </div>
    );
}