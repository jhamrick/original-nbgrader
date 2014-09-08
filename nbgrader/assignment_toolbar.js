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

        getCellType = function (cell) {
            if (cell.metadata.assignment === undefined) {
                return "-";
            } else {
                return cell.metadata.assignment.cell_type;
            }
        },

        updateGradeable = function (cell, cell_type) {
            var cls = "assignment-gradeable-cell",
                elem = cell.element;

            if (elem && cell_type === "grade" && !elem.hasClass(cls)) {
                elem.addClass(cls);
            } else if (elem && cell_type !== "grade" && elem.hasClass(cls)) {
                elem.removeClass(cls);
            }
        },

        updatePoints = function (cell, cell_type, points_elem) {
            var elem = cell.element;

            if (elem) {
                if (!points_elem) {
                    points_elem = elem.find(".assignment-points");
                }

                if (cell_type === "grade") {
                    points_elem.show();
                } else {
                    points_elem.hide();
                }
            }
        },

        updateId = function (cell, cell_type, id_elem) {
            var elem = cell.element;

            if (elem) {
                if (!id_elem) {
                    id_elem = elem.find(".assignment-id");
                }

                if (cell_type === "grade") {
                    id_elem.show();
                } else {
                    id_elem.hide();
                }
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
                var cell_type = getCellType(cell);
                updateGradeable(cell, cell_type);
                updatePoints(cell, cell_type);
                updateId(cell, cell_type);
            },

            function (cell) {
                var cell_type = getCellType(cell);
                updateGradeable(cell, cell_type);
                updatePoints(cell, cell_type);
                updateId(cell, cell_type);
                return cell_type;
            }
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

            var cell_type = getCellType(cell);
            updateGradeable(cell, cell_type);
            updatePoints(cell, cell_type, button_container);
        },

        getId = function (cell) {
            if (cell.metadata.assignment === undefined) {
                return undefined;
            } else {
                return cell.metadata.assignment.id;
            }
        },

        setId = function (cell, value) {
            if (cell.metadata.assignment === undefined) {
                cell.metadata.assignment = {};
            }
            cell.metadata.assignment.id = value;
        },

        id = function (div, cell, celltoolbar) {
            var button_container = $(div);
            button_container.addClass("assignment-id");

            var text = $('<input/>').attr('type', 'text');
            var lbl = $('<label/>').append($('<span/>').text("Problem ID: "));
            lbl.append(text);

            text.addClass("assignment-id-input");
            text.attr("value", getId(cell));
            text.keyup(function(){
                setId(cell, text.val());
            });

            button_container.append($('<span/>').append(lbl));
            IPython.keyboard_manager.register_events(text);

            var cell_type = getCellType(cell);
            updateGradeable(cell, cell_type);
            updateId(cell, cell_type, button_container);
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
            CellToolbar.register_callback('create_assignment.id', id);

            var create_preset = [
                'create_assignment.select', 
                'create_assignment.points',
                'create_assignment.id'
            ];

            CellToolbar.register_preset('Create Assignment', create_preset, notebook);
            console.log('Assignment extension for metadata editing loaded.');

            // update css class for whether cells are gradeable
            var cells = IPython.notebook.get_cells();
            for (var i = 0; i < cells.length; i++) {
                updateGradeable(cells[i], getCellType(cells[i]));
            }
        };

    return {'register': register};
});
