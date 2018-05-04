using System;
using System.Collections;
using System.Collections.Generic;
using System.Net;
using System.Text;
using UnityEngine;
using uPLibrary.Networking.M2Mqtt;

public class WaypointsScript : MonoBehaviour {
    // MQTT client used to publish waypoints to server
    public MqttClient client;
    // Topics on mqtt client to subscribe/publish to
    string publishLocationsTopic = "vopwaypoints";
    // ip-address of mqtt server
    public static IPAddress ip;
    // list of all available drones
    ArrayList droneIDs = new ArrayList();
    // Int's to add waypoints (these are coordinates) and int to specify target drone
    public int x,y,z,target;
    // Timers for error messages
    float errorDisplayTime = 3f;
    float waypointErrorTimer, lineErrorTimer, targetErrorTimer;
    // Waypoint object to add to scene
    public GameObject WayPoint;
    // GUIStyle to style error messages
    public GUIStyle errorStyle;
    // Contains all waypoints for current route that are created through the "add waypoint" button
    ArrayList dynamicWaypoints = new ArrayList();
    // Contains connection lines between waypoints
    ArrayList lines = new ArrayList();
    // Drone needs space to fly
    float flyRadius = 0.1f;

	// Use this for initialization
	void Start () {
        // Read variables from config file
        Setup();
        // Initialize timers
        waypointErrorTimer = 0f;
        lineErrorTimer = 0f;
        // Styling of error messages
        errorStyle.normal.textColor = Color.red;
        errorStyle.fontSize = 20;
        errorStyle.fontStyle = FontStyle.Italic;
        /* Setup mqtt client
         * Port is default port so doesnt have to be specified
         * ip-address specified above on port 1883
         */
        client = new MqttClient(ip);
        client.Connect(Guid.NewGuid().ToString());
    }

    // Update is called once per frame
    void Update () {
	}   

    /** Displays error messages */
    void OnGUI ()
    {
        // Display waypoint error
        if (Mathf.CeilToInt(waypointErrorTimer) > 0)
        {
            waypointErrorTimer -= Time.deltaTime;
            GUI.Label(new Rect(50, 20, 100, 25), "Waypoint too close to an obstacle!", errorStyle);
        }
        // Display line error
        if (Mathf.CeilToInt(lineErrorTimer) > 0)
        {
            lineErrorTimer -= Time.deltaTime;
            GUI.Label(new Rect(50, 40, 100, 25), "Impossible trajectory!", errorStyle);
        }
        // Display invalid target error
        if (Mathf.CeilToInt(targetErrorTimer) > 0)
        {
            targetErrorTimer -= Time.deltaTime;
            GUI.Label(new Rect(50, 60, 100, 25), "Target drone doesn't exist!", errorStyle);
        } 
    }

    /** Writes locations of waypoints (in MQTT coordinates and JSON format) to a file with location fileloc*/
    public void WriteWaypointsToFile(string fileloc)
    {
        // Empty file if it should have existed before
        System.IO.File.Delete(fileloc);
		System.IO.File.AppendAllText(fileloc, waypointsToString());
    }

    /** Transforms coordinates from the MQTT coordinate system to unity coordinate system */
    Vector3 TransformCoordinates(Vector3 coords)
    {
        float temp = coords.y;
        coords.y = coords.z;
        coords.z = -temp;

        return coords;
    }

    /** Transforms coordinates from the unity coordinate system to the MQTT coordinate system */
    Vector3 InverseTransformCoordinates(Vector3 coords)
    {
        float temp = coords.y;
        coords.y = -coords.z;
        coords.z = temp;

        return coords;
    }

    /** Prepares everything to be able to start a new route */
    public void newRoute()
    {
        deleteAllLines();
        deleteAllWaypoints();
    }

    /** Draws a line between two points: blue if no collisions red if collisions
     * returns true if no collisions detected
     */
    bool DrawLine(Vector3 start, Vector3 end)
    {
        // Boolean to indicate whether it's an ok trajectory
        bool goodTrajectory = true;
        // GameObject for line
        GameObject connection = new GameObject();
        connection.transform.position = start;
        connection.AddComponent<LineRenderer>();
        LineRenderer lr = connection.GetComponent<LineRenderer>();
        // Check for collisions along the line
        if (Physics.CheckCapsule(start, end, flyRadius))
        {
            // If collision detected indicate by line color
            lr.material.color = Color.red;
            goodTrajectory = false;
        }
		else
        {
            lr.material.color = Color.blue;
        }
        lr.startWidth = 30f;
        lr.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        lr.SetPosition(0, start);
        lr.SetPosition(1, end);
        lines.Add(connection);
        return goodTrajectory;
    }

    /** Draws lines between dynamically created waypoints, returns true if no collisions */
    public bool DrawAllLines()
    {
        bool goodTrajectory = true;
        RemoveColliders();
        for (int i=0; i<dynamicWaypoints.Count-1; i++)
        {
            GameObject w1 = (GameObject)dynamicWaypoints[i];
            GameObject w2 = (GameObject)dynamicWaypoints[i + 1];
            bool noCollision = DrawLine(w1.transform.position, w2.transform.position);
            if (!noCollision) goodTrajectory = false;
        }
        addColliders();
        return goodTrajectory;
    }

    public void deleteAllWaypoints()
    {
        for(int i=0; i<dynamicWaypoints.Count; i++)
        {
            GameObject waypoint = (GameObject)dynamicWaypoints[i];
            Destroy(waypoint);
        }
        dynamicWaypoints.Clear();
    }

    /** Destroys all lines */
    public void deleteAllLines()
    {
        for(int i=0; i<lines.Count; i++)
        {
            GameObject line = (GameObject)lines[i];
            Destroy(line);
        }
        lines.Clear();
    }

    /** Removes colliders from waypoints */
    public void RemoveColliders()
    {
        for(int i=0; i<dynamicWaypoints.Count; i++)
        {
            GameObject waypoint = (GameObject)dynamicWaypoints[i];
            waypoint.GetComponent<SphereCollider>().enabled = false;
        }
    }

    /** Adds colliders to waypoints */
    public void addColliders()
    {
        for (int i = 0; i < dynamicWaypoints.Count; i++)
        {
            GameObject waypoint = (GameObject)dynamicWaypoints[i];
            waypoint.GetComponent<SphereCollider>().enabled = true;
        }
    }
    /** Draws lines to visualize trajectory and sends waypoint coordinates to a MQTT server if no collisions on path*/
    public void takeoff()
    {
        deleteAllLines();
        bool okRoute = DrawAllLines();
        bool validTarget = droneIDs.Contains(target);
        if (okRoute && validTarget)
        {
            // Publish waypoint coordinates to the mqtt server on topic specified above
			client.Publish(publishLocationsTopic, Encoding.UTF8.GetBytes(waypointsToString()));
			// Write waypoints to a file in JSON format
			WriteWaypointsToFile(Application.dataPath + "/Waypoints/Waypoints.json");
        }
		else if(!okRoute)
        {
            lineErrorTimer = errorDisplayTime;
        }else if (!validTarget)
        {
            targetErrorTimer = errorDisplayTime;
        }
    }

    /** Makes a JSON formatted string containing all waypoint locations and ID in order */
    public string waypointsToString()
    {
        string locations = "{\n\t\"target\": "+ target+ ",\n";
        locations+= "\t\"waypoints\": [\n";
        for(int i=0; i<dynamicWaypoints.Count; i++)
        {
            GameObject wp = (GameObject)dynamicWaypoints[i];
            Vector3 position = InverseTransformCoordinates(wp.transform.position);
            locations += "\t\t{\n\t\t\t\"ID\": " + i + ",\n";
            locations += "\t\t\t\"position\": {\n";
            locations += "\t\t\t\t\"x\": " + position.x +",\n";
            locations += "\t\t\t\t\"y\": " + position.y + ",\n";
            locations += "\t\t\t\t\"z\": " + position.z + "\n";
            locations += "\t\t\t}\n";
            locations += "\t\t}";
            if (i != dynamicWaypoints.Count - 1)
            {
                locations += ",";
            }
            locations += "\n";
        }
        locations += "\t]\n}";

        return locations;
    }

    /** Adds a waypoint on specified coordinates (MQTT coordinates)
     * unless it's too close to an obstacle or it's the same location as previous waypoint
     */
    public void addDynamicWayPoint()
    {
        // Position where it should go in unity coordinates
        Vector3 unityCoords = TransformCoordinates(new Vector3(x, y, z));
        // Check if not same location as previous waypoint
        bool sameWaypoint = false;
        if (dynamicWaypoints.Count > 0)
        {
            GameObject previousWaypoint = (GameObject)dynamicWaypoints[dynamicWaypoints.Count - 1];
            if (previousWaypoint.transform.position == unityCoords) sameWaypoint = true;
        }
        // Check if there is an obstacle at that position, display error if there is
        if (Physics.CheckSphere(unityCoords, flyRadius))
        {
            waypointErrorTimer = errorDisplayTime;
        }
		else if (!sameWaypoint)
        {
            // If no obstacle and not the same waypoint as the previous: put waypoint there
            waypointErrorTimer = 0f;
            GameObject waypoint = Instantiate(WayPoint, unityCoords, Quaternion.identity);
            // Add script to make waypoint dragable
            waypoint.AddComponent<DragScript>();
            waypoint.AddComponent<SphereCollider>();
            dynamicWaypoints.Add(waypoint);
        }
    }

    /** Changes x coordinate of new waypoint */
    public void changeX(string x)
    {
        this.x = int.Parse(x);
    }

    /** Changes y coordinate of new waypoint */
    public void changeY(string y)
    {
        this.y = int.Parse(y);
    }

    /** Changes z coordinate of new waypoint */
    public void changeZ(string z)
    {
        this.z = int.Parse(z);
    }

    /** Changes target drone for route */
    public void changeTarget(string target)
    {
        this.target = int.Parse(target);
    }

    /** Setup all variables from config JSON file */
    public void Setup()
    {
        string[] config = System.IO.File.ReadAllLines(Application.dataPath + "/Config/Config.json");
        foreach(string line in config)
        {
            if (line.Contains("ip"))
            {
                string ipaddress = line.Split(':')[1].Split('"')[1];
                ip = IPAddress.Parse(ipaddress);
            }
            else if (line.Contains("flyradius"))
            {
                float radius = float.Parse(line.Split(':')[1].Split('"')[1]);
                flyRadius = radius;
            }else if (line.Contains("waypointstopic"))
            {
                publishLocationsTopic = line.Split(':')[1].Split('"')[1];
            }else if (line.Contains("id"))
            {
                int id = Int32.Parse(line.Split(':')[1].Split('"')[1]);
                droneIDs.Add(id);
            }
        }
    }
}
