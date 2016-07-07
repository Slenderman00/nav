define(function(require, exports, module) {
  var _ = require("libs/underscore");
  var Foundation = require("libs/foundation.min");
  var Backbone = require("backbone");
  var Marionette = require("marionette");

  var Models = require("src/ipam/models");
  var viz = require("src/ipam/viz");

  // Global communication channel with main app
  var globalCh = Backbone.Wreqr.radio.channel("global");
  var debugCh = Backbone.Wreqr.radio.channel("debug");

  // Utility function to flash global messages
  function flash(klass, msg) {
    globalCh.vent.trigger("flash", klass, msg);
  }

  function _debug(namespace) {
    return function() {
      debugCh.vent.trigger("debug", namespace, arguments);
    };
  }

  var debug = require("src/ipam/util").debug;

  // Subview for available subnets for the current prefix/scope
  var AvailableSubnetsView = Marionette.ItemView.extend({
    debug: debug("views:available_subnets"),
    template: "#prefix-available-subnets",
    events: {
      "click .fetch-subnets": "fetch",
      "click .hide-subnets": "hide"
    },

    modelEvents: {
      "change": "render"
    },

    initialize: function(opts) {
      this.model = new Models.AvailableSubnets({
        queryParams: {
          prefix: opts.prefix
        }
      });
      debug("Mounted subnet component for " + opts.prefix);
    },

    hide: function(evt) {
      evt.preventDefault();
      evt.stopPropagation();
      this.$el.find(".subnets:first").hide();
      this.model.set("hide", true);
    },

    fetch: function(evt) {
      evt.preventDefault();
      evt.stopPropagation();
      this.refetch();
    },

    refetch: function() {
      var prefix = this.model.get("queryParams").prefix;
      this.debug("Trying to get subnets for " + prefix);
      // cache xhr object
      this.xhr = this.model.fetch({reset: true});
      this.xhr.done(this.render);
    }
  });

  // Control form for tree
  var ControlView = Marionette.ItemView.extend({
    template: "#prefix-control-form",
    events: {
      "input .prefix-tree-query": "updateSearch",
      "change .search-param": "updateSearch"
    },

    _updateSearch: function() {
      var params = {};
      // handle check boxes
      var checked = this.$el.find("input.search-param:checked");
      checked.each(function() {
        var elem = $(this);
        var param = elem.attr("name");
        var param_field = params[param] || [];
        param_field.push(elem.val());
        params[param] = param_field;
      });
      // handle search string
      params["search"] = this.$el.find(".prefix-tree-query").val();
      // handle date ranges
      params["starttime"] = this.$el.find("#usage_start").val();
      params["endtime"] = this.$el.find("#usage_end").val();
      globalCh.vent.trigger("search:update", params);
    },

    initialize: function() {
      this.updateSearch = _.throttle(this._updateSearch, 1000);
    }

  });

  // Base of tree
  var RootView = Marionette.LayoutView.extend({
    debug: debug("views:rootview"),
    regions: {
      "tree": ".prefix-tree-root"
    },
    template: "#prefix-list",

    // Check if we have an empty tree
    isEmpty: function() {
      return !this.collection || this.collection.length === 0;
    },

    /* Refetch collection */
    refetch: function() {
      // Cancel existing fetches to avoid happy mistakes
      if (typeof this.xhr !== "undefined") {
        this.debug("Aborted previous fetch!");
        this.xhr.abort();
      }
      // Keep a pointer to the fetch object, for tracking all fetches
      this.xhr = this.collection.fetch({reset: true});
      flash("alert-box", "Fetching...");
    },

    initialize: function() {
      // Don't mess with the ordering
      this.sort = false;
      // Don't render before fetch of collection returns
      this.collection = new Models.PrefixNodes();
      this.refetch();
      // Handle reset events, e.g. when a fetch is done
      this.collection.bind("reset", this.onRender, this);
      this.collection.bind("fetch", this.onRender, this);
      // Set up global handlers for requests etc
      var self = this;
      globalCh.vent.on("fetch:all", function() { self.refetch(); });

      // Handle updated params
      globalCh.vent.on("search:update", function(params) {
        debug("Got new search params", params);
        self.collection.queryParams = params;
        self.refetch();
      });
    },

    /* Whether or not we're currently fetching some data */
    isFetching: function() {
      if (typeof this.xhr === "undefined") {
        return false;
      }
      switch (this.xhr.readyState) {
      case 1:
      case 2:
      case 3:
        return true;
      default:
        return false;
      }
    },

    onBeforeShow: function() {
      this.showChildView("tree", new TreeView({
        collection: this.collection
      }));
    },

    onRender: function() {
      if (this.isFetching()) {
        return flash("alert-box", "Fetching...");
      }
      // TODO: show load/fetch messages
      if (this.isEmpty()) {
        var template = _.template("No results<% if (query) { %> for <strong>'<%- query %>'</strong><% } %>.");
        var searchParams = this.collection.queryParams.search;
        return flash("alert-box alert with-icon", template({query: searchParams }));
      } else {
        return globalCh.vent.trigger("flash:reset");
      }
    }

  });

  // TODO: Fetch available subnets, see available_subnets in prefix_tree.py
  var NodeView = Marionette.LayoutView.extend({
    debug: debug("views:nodeview"),
    tagName: "li",
    className: "prefix-tree-item",
    template: "#prefix-tree-node",

    regions: {
      usage_graph: ".prefix-usage-graph:first",
      children: ".prefix-tree-children-container",
      available_subnets: ".prefix-tree-available-subnets:first"
    },

    events: {
      "click a.prefix-tree-item-title": "toggleOpen",
      "touchstart a.prefix-tree-item-title": "toggleOpen"
    },

    childEvents: {
      'update:dhcp_treshold': "dhcpChange"
    },

    // Hide/show element
    toggleOpen: function(evt) {
      // avoid bubbling up to parent, as we're dealing with nested views
      evt.preventDefault();
      evt.stopPropagation();
      // open content
      var content = this.$el.find(".prefix-tree-item-content:first");
      var title = this.$el.find(".prefix-tree-item-title:first");
      content.slideToggle(200);//.toggleClass("prefix-item-open");
      title.toggleClass("prefix-item-open");
      // deferred rendering of children
      if (!this.model.hasShownChildren() && this.model.hasChildren()) {
        this.showChildren();
      }
      this.debug("Toggle " + this.model.get("pk"));
    },

    dhcpChange: function() {
      console.log("wææææ, treshold changed!");
    },

    // We defer drawing children to return a shallow tree faster to the user
    showChildren: function() {
      this.debug("Rendering children for " + this.model.get("pk"));
      var children = this.model.children;
      this.showChildView("children", new TreeView({
        collection: children
      }));
      this.model.set("hasShownChildren", true);
    },

    onBeforeShow: function() {
      var utilization = this.model.get("utilization");
      this.showChildView("usage_graph", new UsageGraph({
        utilization: utilization
      }));
      // Mount subnet component
      var prefix = this.model.get("prefix");
      this.showChildView("available_subnets", new AvailableSubnetsView({
        prefix: prefix
      }));
    }

  });

  /* Dumb view for mounting usage graph */
  var UsageGraph = Marionette.View.extend({
    debug: debug("views:usagegraph"),
    // mock - for catching dhcp treshold change in parent?
    triggers: {
      "click svg": "update:dhcp_treshold"
    },

    initialize: function(opts) {
      this.utilization = opts.utilization;
    },

    onBeforeShow: function() {
      this.debug("Trying to draw usage graph");
      var usageElem = this.$el.find(".prefix-usage-graph");
      var template = _.template("<span>Usage: <%= percent %> %</span>");
      this.$el.html(template({percent: (this.utilization * 100).toFixed(2)}));
      viz.usageChart({
        mountElem: this.$el.get(0),
        width: 100,
        height: 10,
        data: [{
          fill: "lightsteelblue",
          name: "Available",
          value: 1.0 - this.utilization
        },{
          fill: "white",
          name: "Used",
          value: this.utilization
        }]
      });
    }
  });

  // Dumb container for prefix nodes, nested or otherwise
  var TreeView = Marionette.CompositeView.extend({
    template: "#prefix-children",
    childView: NodeView,
    childViewContainer: ".prefix-tree-children"
  });

  module.exports = {
    "NodeView": NodeView,
    "ControlView": ControlView,
    "RootView": RootView
  };

});
