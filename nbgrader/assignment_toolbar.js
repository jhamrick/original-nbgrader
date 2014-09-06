/*global define */

define([
    'jquery',
    'notebook/js/celltoolbar',

], function ($, celltoolbar) {
    "use strict";

    var CellToolbar = celltoolbar.CellToolbar,
        select_type = CellToolbar.utils.select_ui_generator(
            [
                ["-"             , "-"        ],
                ["To be graded"  , "grade"    ],
                ["Release only"  , "release"  ],
                ["Solution only" , "solution" ],
                ["Skip"          , "skip"     ],
            ],

            function (cell, value) {
                if (cell.metadata.assignment === undefined) {
                    cell.metadata.assignment = {};
                }
                cell.metadata.assignment.cell_type = value;
            },

            function (cell) {
                if (cell.metadata.assignment === undefined) {
                    return "-";
                } else {
                    return cell.metadata.assignment.cell_type;
                }
            }
        ),

        points = CellToolbar.utils.input_ui_generator(
            "Points: ",
            function (cell, value) {
                if (cell.metadata.assignment === undefined) {
                    cell.metadata.assignment = {};
                }
                cell.metadata.assignment.points = value;
                console.log("points: " + value);
            },

            function (cell) {
                if (cell.metadata.assignment === undefined) {
                    return undefined;
                } else {
                    return cell.metadata.assignment.points;
                }
            },

            "3em"
        ),

        load_ipython_extension = function (notebook) {
            CellToolbar.register_callback('create_assignment.select', select_type);
            CellToolbar.register_callback('create_assignment.points', points);

            var create_preset = ['create_assignment.select', 'create_assignment.points'];
            CellToolbar.register_preset('Create Assignment', create_preset, notebook);

            console.log('Assignment extension for metadata editing loaded.');
        };

    return {'load_ipython_extension': load_ipython_extension};
});

