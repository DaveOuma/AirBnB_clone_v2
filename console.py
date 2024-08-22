#!/usr/bin/python
"""
Module for console
"""
import cmd
import re
import shlex
import ast
from models import storage
from models.base_model import BaseModel
from models.user import User
from models.amenity import Amenity
from models.place import Place
from models.review import Review
from models.state import State
from models.city import City


def split_curly_braces(e_arg):
    """
    Splits the curly braces for the update method
    """
    curly_braces = re.search(r"\{(.*?)\}", e_arg)

    if curly_braces:
        id_with_comma = shlex.split(e_arg[:curly_braces.span()[0]])
        id = [i.strip(",") for i in id_with_comma][0]

        str_data = curly_braces.group(1)
        try:
            arg_dict = ast.literal_eval("{" + str_data + "}")
        except Exception:
            print("** invalid dictionary format **")
            return
        return id, arg_dict
    else:
        commands = e_arg.split(",")
        if commands:
            try:
                id = commands[0]
            except Exception:
                return "", ""
            try:
                attr_name = commands[1]
            except Exception:
                return id, ""
            try:
                attr_value = commands[2]
            except Exception:
                return id, attr_name
            return f"{id}", f"{attr_name} {attr_value}"


class HBNBCommand(cmd.Cmd):
    """
    HBNBCommand console class
    """
    prompt = "(hbnb) "
    valid_classes = ["BaseModel", "User", "Amenity", "Place", "Review", "State", "City"]

    def emptyline(self):
        """
        Do nothing when an empty line is entered.
        """
        pass

    def do_EOF(self, arg):
        """
        EOF (Ctrl+D) signal to exit the program.
        """
        return True

    def do_quit(self, arg):
        """
        Quit command to exit the program.
        """
        return True

    def do_create(self, arg):
        """
        Create a new instance of BaseModel and save it to the JSON file.
        Usage: create <class_name> <key1=value1> <key2=value2> ...
        """
        try:
            if not arg:
                print("** class name missing **")
                return
            
            commands = shlex.split(arg)
            class_name = commands[0]

            if class_name not in self.valid_classes:
                print("** class doesn't exist **")
                return

            kwargs = {}
            for command in commands[1:]:
                key, value = command.split("=")
                if value.startswith('"') and value.endswith('"'):
                    value = value.strip('"').replace("_", " ")
                else:
                    try:
                        value = ast.literal_eval(value)
                    except (SyntaxError, ValueError):
                        continue
                kwargs[key] = value

            # Create a new instance of the class
            new_instance = eval(class_name)(**kwargs)
            storage.new(new_instance)
            storage.save()
            print(new_instance.id)

        except Exception as e:
            print(f"Error: {e}")

    def do_show(self, arg):
        """
        Show the string representation of an instance.
        Usage: show <class_name> <id>
        """
        commands = shlex.split(arg)

        if len(commands) == 0:
            print("** class name missing **")
        elif commands[0] not in self.valid_classes:
            print("** class doesn't exist **")
        elif len(commands) < 2:
            print("** instance id missing **")
        else:
            objects = storage.all()
            key = "{}.{}".format(commands[0], commands[1])
            if key in objects:
                print(objects[key])
            else:
                print("** no instance found **")

    def do_destroy(self, arg):
        """
        Delete an instance based on the class name and id.
        Usage: destroy <class_name> <id>
        """
        commands = shlex.split(arg)

        if len(commands) == 0:
            print("** class name missing **")
        elif commands[0] not in self.valid_classes:
            print("** class doesn't exist **")
        elif len(commands) < 2:
            print("** instance id missing **")
        else:
            objects = storage.all()
            key = "{}.{}".format(commands[0], commands[1])
            if key in objects:
                del objects[key]
                storage.save()
            else:
                print("** no instance found **")

    def do_all(self, arg):
        """
        Print the string representation of all instances or a specific class.
        Usage: <User>.all()
                <User>.show()
        """
        objects = storage.all()

        commands = shlex.split(arg)

        if len(commands) == 0:
            for key, value in objects.items():
                print(str(value))
        elif commands[0] not in self.valid_classes:
            print("** class doesn't exist **")
        else:
            for key, value in objects.items():
                if key.split('.')[0] == commands[0]:
                    print(str(value))
        
    def do_count(self, arg):
        """
        Counts and retrieves the number of instances of a class
        usage: <class name>.count()
        """
        objects = storage.all()

        commands = shlex.split(arg)

        if arg:
            incoming_class_name = commands[0]
        count = 0

        if commands:
            if incoming_class_name in self.valid_classes:
                for obj in objects.values():
                    if obj.__class__.__name__ == incoming_class_name:
                        count += 1
                print(count)
            else:
                print("** invalid class name **")
        else:
            print("** class name missing **")

    def do_update(self, arg):
        """
        Update an instance by adding or updating an attribute.
        Usage: update <class_name> <id> <attribute_name> "<attribute_value>"
        """
        commands = shlex.split(arg)

        if len(commands) == 0:
            print("** class name missing **")
        elif commands[0] not in self.valid_classes:
            print("** class doesn't exist **")
        elif len(commands) < 2:
            print("** instance id missing **")
        else:
            objects = storage.all()
            key = "{}.{}".format(commands[0], commands[1])
            if key not in objects:
                print("** no instance found **")
            elif len(commands) < 3:
                print("** attribute name missing **")
            elif len(commands) < 4:
                print("** value missing **")
            else:
                obj = objects[key]
                curly_braces = re.search(r"\{(.*?)\}", arg)

                if curly_braces:
                    # Handle dictionary updates
                    try:
                        str_data = curly_braces.group(1)
                        arg_dict = ast.literal_eval("{" + str_data + "}")

                        for attr_name, attr_value in arg_dict.items():
                            setattr(obj, attr_name, attr_value)
                        obj.save()
                    except Exception as e:
                        print(f"** error updating attributes: {e} **")
                else:
                    attr_name = commands[2]
                    attr_value = commands[3]

                    try:
                        attr_value = eval(attr_value)
                    except (NameError, SyntaxError):
                        pass  # attr_value remains a string if eval fails
                    
                    try:
                        setattr(obj, attr_name, attr_value)
                        obj.save()
                    except Exception as e:
                        print(f"** error updating attribute: {e} **")

    def default(self, arg):
        """
        Default behavior for cmd module when input is invalid
        """
        arg_list = arg.split('.')

        if len(arg_list) != 2:
            print("*** Unknown syntax: {}".format(arg))
            return

        cls_nm = arg_list[0]  # incoming class name
        command = arg_list[1].split('(')
        cmd_met = command[0]  # incoming command method

        if len(command) < 2:
            e_arg = ""
        else:
            e_arg = command[1].split(')')[0]  # extra arguments

        method_dict = {
            'all': self.do_all,
            'show': self.do_show,
            'destroy': self.do_destroy,
            'update': self.do_update,
            'count': self.do_count
        }

        if cmd_met in method_dict.keys():
            if cmd_met != "update":
                return method_dict[cmd_met]("{} {}".format(cls_nm, e_arg))
            else:
                if not cls_nm:
                    print("** class name missing **")
                    return
                try:
                    obj_id, arg_dict = split_curly_braces(e_arg)
                    call = method_dict[cmd_met]
                    return call("{} {} {}".format(cls_nm, obj_id, arg_dict))
                except Exception as e:
                    print(f"** error processing update command: {e} **")
        else:
            print("*** Unknown syntax: {}".format(arg))
            return False


if __name__ == '__main__':
    HBNBCommand().cmdloop()