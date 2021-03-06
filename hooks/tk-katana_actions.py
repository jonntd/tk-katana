"""
Hook that loads defines all the available actions, broken down by publish type.
Copied from tk-maya_actions
"""
import sgtk
import os
import NodegraphAPI

HookBaseClass = sgtk.get_hook_baseclass()

class KatanaActions(HookBaseClass):

    def generate_actions(self, sg_publish_data, actions, ui_area):
        """
        Returns a list of action instances for a particular publish.
        This method is called each time a user clicks a publish somewhere in the UI.
        The data returned from this hook will be used to populate the actions menu for a publish.
    
        The mapping between Publish types and actions are kept in a different place
        (in the configuration) so at the point when this hook is called, the loader app
        has already established *which* actions are appropriate for this object.
        
        The hook should return at least one action for each item passed in via the 
        actions parameter.
        
        This method needs to return detailed data for those actions, in the form of a list
        of dictionaries, each with name, params, caption and description keys.
        
        Because you are operating on a particular publish, you may tailor the output 
        (caption, tooltip etc) to contain custom information suitable for this publish.
        
        The ui_area parameter is a string and indicates where the publish is to be shown. 
        - If it will be shown in the main browsing area, "main" is passed. 
        - If it will be shown in the details area, "details" is passed.
        - If it will be shown in the history area, "history" is passed. 
        
        Please note that it is perfectly possible to create more than one action "instance" for 
        an action! You can for example do scene introspection - if the action passed in 
        is "character_attachment" you may for example scan the scene, figure out all the nodes
        where this object can be attached and return a list of action instances:
        "attach to left hand", "attach to right hand" etc. In this case, when more than 
        one object is returned for an action, use the params key to pass additional 
        data into the run_action hook.
        
        :param sg_publish_data: Shotgun data dictionary with all the standard publish fields.
        :param actions: List of action strings which have been defined in the app configuration.
        :param ui_area: String denoting the UI Area (see above).
        :returns List of dictionaries, each with keys name, params, caption and description
        """
        app = self.parent
        app.log_debug("Generate actions called for UI element %s. "
                      "Actions: %s. Publish Data: %s" % (ui_area, actions, sg_publish_data))
        
        action_instances = []
        
        if "open_project" in actions:
            action_instances.append( {"name": "open_project", 
                                      "params": None,
                                      "caption": "Open Project", 
                                      "description": "This will open the Katana project file."} )

        if "import_look_file" in actions:
            action_instances.append( {"name": "import_look_file", 
                                      "params": None,
                                      "caption": "Import Look File", 
                                      "description": "This will create an LookFileAssign node corresponding to this published Look File."} )

        if "create_node_Alembic_In" in actions:
            action_instances.append( {"name": "create_node_Alembic_In", 
                                      "params": None,
                                      "caption": "Import Alembic", 
                                      "description": "This will create an Alembic_In node corresponding to this cache."} )

        if "create_node_ImageRead" in actions:
            action_instances.append( {"name": "create_node_ImageRead",
                                      "params": None, 
                                      "caption": "Import image", 
                                      "description": "Creates an ImageRead node for the selected item."} )

        return action_instances


    def execute_action(self, name, params, sg_publish_data):
        """
        Execute a given action. The data sent to this be method will
        represent one of the actions enumerated by the generate_actions method.
        
        :param name: Action name string representing one of the items returned by generate_actions.
        :param params: Params data, as specified by generate_actions.
        :param sg_publish_data: Shotgun data dictionary with all the standard publish fields.
        :returns: No return value expected.
        """
        app = self.parent
        app.log_debug("Execute action called for action %s. "
                      "Parameters: %s. Publish Data: %s" % (name, params, sg_publish_data))
        
        # resolve path
        path = self.get_publish_path(sg_publish_data)
        
        if name == "open_project":
            self._open_project(path, sg_publish_data)

        if name == "import_look_file":
            self._open_project(path, sg_publish_data)

        if name == "create_node_Alembic_In":
            self._create_node("Alembic_In", path, sg_publish_data, asset_parameter="abcAsset")
        
        if name == "create_node_ImageRead":
            self._create_node("ImageRead", path, sg_publish_data, asset_parameter="file")


    ##############################################################################################################
    # helper methods which can be subclassed in custom hooks to fine tune the behaviour of things

    def _open_project(self, path, sg_publish_data):
        """
        """
        return

    def _create_node(self, node_type, path, sg_publish_data, asset_parameter="file"):
        """
        Generic node creation method.
        """
        if not os.path.exists(path):
            raise Exception("File not found on disk - '%s'" % path)
                
        project_path = "/mnt/netdev/sam.saxon/shotgun/Shotgun_Katana_Test/big_buck_bunny" # TODO: Hardcoded == not cool
        tk = sgtk.tank_from_path( project_path )

        # Setup shotgun asset string
        template = tk.template_from_path( path )
        fields = template.get_fields( path )
        # TODO Temporary fix for the SEQ field which seems to mess up the search
        if fields.has_key("SEQ"):
            fields.pop("SEQ")
        parameter_dict = {}
        parameter_dict["template"] = template.name
        parameter_dict["fields"] = fields

        # Create node
        root = NodegraphAPI.GetRootNode()
        node = NodegraphAPI.CreateNode(node_type, parent=root)
        parm = node.getParameter(asset_parameter)
        parm.setValue(str(parameter_dict), 0)
        return node


