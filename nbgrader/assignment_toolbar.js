/*global define, require */

define([
    'jquery',
    'notebook/js/celltoolbar',

], function ($, celltoolbar) {
    "use strict";

    var CellToolbar = celltoolbar.CellToolbar,

        handleCellType = function (cell, cell_type) {
            if (cell_type === "grade") {
                cell.celltoolbar.inner_element.find(".assignment-points").show();
                cell.element.addClass("assignment-gradeable-cell");
            } else {
                cell.celltoolbar.inner_element.find(".assignment-points").hide();
                cell.element.removeClass("assignment-gradeable-cell");
            }
        },

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
                handleCellType(cell, value);
            },

            function (cell) {
                var cell_type;
                if (cell.metadata.assignment === undefined) {
                    cell_type = "-";
                } else {
                    cell_type = cell.metadata.assignment.cell_type;
                }
                handleCellType(cell, cell_type);
                return cell_type;
            }
        ),

        points = function (div, cell, celltoolbar) {
            var f = CellToolbar.utils.input_ui_generator(
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
            );

            $(div).addClass("assignment-points");
            f(div, cell, celltoolbar);
        },

        load_css = function () {
            var link = document.createElement("link");
            link.type = "text/css";
            link.rel = "stylesheet";
            link.href = "/nbextensions/assignment.css";
            console.log(link);
            document.getElementsByTagName("head")[0].appendChild(link);
        },

        register = function (notebook) {
            load_css();
            CellToolbar.register_callback('create_assignment.select', select_type);
            CellToolbar.register_callback('create_assignment.points', points);

            var create_preset = ['create_assignment.points', 'create_assignment.select'];
            CellToolbar.register_preset('Create Assignment', create_preset, notebook);
            console.log('Assignment extension for metadata editing loaded.');
        };

    return {'register': register};
});
