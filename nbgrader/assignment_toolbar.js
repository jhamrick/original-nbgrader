/*global define, require */
/**
 * To load this extension, add the following to your custom.js:
 *
 * $([IPython.events]).on('app_initialized.NotebookApp', function() {
 *     require(["nbextensions/assignment"], function (assignment) {
 *         console.log('Assignment extension loaded');
 *         assignment.register(IPython.notebook);
 *     });
 * });
 *
**/

define([
    'base/js/namespace',
    'jquery',
    'notebook/js/celltoolbar',

], function (IPython, $, celltoolbar) {
    "use strict";

    var CellToolbar = celltoolbar.CellToolbar,

        handleCellType = function (cell, points_elem) {
            var cls = "assignment-gradeable-cell",
                elem = cell.element,
                cell_type;

            if (cell.metadata.assignment === undefined) {
                cell_type = "-";
            } else {
                cell_type = cell.metadata.assignment.cell_type;
            }

            if (!points_elem) {
                points_elem = elem.find(".assignment-points");
            }

            if (elem && cell_type === "grade") {
                points_elem.show();
                if (elem && !elem.hasClass(cls)) {
                    elem.addClass(cls);
                }

            } else if (elem) {
                points_elem.hide();
                if (elem && elem.hasClass(cls)) {
                    elem.removeClass(cls);
                }
            }

            return cell_type;
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
                handleCellType(cell);
            },

            handleCellType
        ),

        getPoints = function (cell) {
            if (cell.metadata.assignment === undefined) {
                return undefined;
            } else {
                return cell.metadata.assignment.points;
            }
        },

        setPoints = function (cell, value) {
            if (cell.metadata.assignment === undefined) {
                cell.metadata.assignment = {};
            }
            cell.metadata.assignment.points = value;
            console.log("points: " + value);
        },

        points = function (div, cell, celltoolbar) {
            var button_container = $(div);
            button_container.addClass("assignment-points");

            var text = $('<input/>').attr('type', 'text');
            var lbl = $('<label/>').append($('<span/>').text("Points: "));
            lbl.append(text);

            text.addClass("assignment-points-input");
            text.attr("value", getPoints(cell));
            text.keyup(function(){
                setPoints(cell, text.val());
            });

            button_container.append($('<span/>').append(lbl));
            IPython.keyboard_manager.register_events(text);

            handleCellType(cell, button_container);
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

            var create_preset = ['create_assignment.select', 'create_assignment.points'];
            CellToolbar.register_preset('Create Assignment', create_preset, notebook);
            console.log('Assignment extension for metadata editing loaded.');
        };

    return {'register': register};
});
