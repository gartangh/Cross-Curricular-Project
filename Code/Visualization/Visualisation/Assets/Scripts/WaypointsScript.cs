using System;
using System.Collections;
using System.Collections.Generic;
using System.Net;
using System.Text;
using UnityEngine;
using uPLibrary.Networking.M2Mqtt;

public class WaypointsScript : MonoBehaviour {
    //MQTT client used to publish waypoints to server
    public MqttClient client;
    //ip-address of mqtt server
    public static IPAddress ip = IPAddress.Parse("157.193.214.115");
    //int's to add waypoints (these are coordinates)
    public int x,y,z;
    //timers for error messages
    float waypointerrortimer;
    float lineerrortimer;
    //if line collides it should not push waypoints to drone
    bool lineCollides;
    //Waypoint object to add to scene
    public GameObject WayPoint;
    //GUIStyle to style error messages
    public GUIStyle errorstyle;
    //Contains all waypoints that are created through the "add waypoint" button
    ArrayList dynamicWaypoints = new ArrayList();
    //drone needs space to fly
    float flyRadius = 0.1f;


	// Use this for initialization
	void Start () {
        //initialize error message timers
        waypointerrortimer = 0f;
        lineerrortimer = 0f;
        //styling of error messages
        errorstyle.normal.textColor = Color.red;
        errorstyle.fontSize = 20;
        errorstyle.fontStyle = FontStyle.Italic;
        //setup mqtt client
        // port is default port so doesnt have to be specified
        // 157.193.214.115 port 1883
        client = new MqttClient(ip);
        client.Connect(Guid.NewGuid().ToString());
    }

    // Update is called once per frame
    void Update () {
        // waypoint collides?
        if (waypointerrortimer > 0)
        {
            waypointerrortimer -= Time.deltaTime;
        }
        // line collides?
        if (lineerrortimer > 0)
        {
            lineerrortimer -= Time.deltaTime;
        }
	}   

    // displays error messages
    void OnGUI ()
    {
        // display waypoint error
        if (Mathf.CeilToInt(waypointerrortimer)>0)
        {
            GUI.Label(new Rect(50, 50, 100, 25), "Waypoint too close to an obstacle!", errorstyle);
        }
        // display line error
        if (Mathf.CeilToInt(lineerrortimer) > 0)
        {
            GUI.Label(new Rect(50, 50, 100, 25), "Impossible trajectory!", errorstyle);
        }
    }

    /**Writes locations of waypoints (in MQTT coordinates) to a file with location fileloc*/
    public void WriteWaypointsToFile(string fileloc)
    {
        // empty file if it should have existed before
        System.IO.File.Delete(fileloc);
        string lines = waypointsToString();
        System.IO.File.AppendAllText(fileloc, lines);
    }

    /**Transforms coordinates from the MQTT coordinate system to unity coordinate system */
    Vector3 TransformCoordinates(Vector3 coords)
    {
        float temp = coords.y;
        coords.y = coords.z;
        coords.z = -temp;
        return coords;
    }

    /**Transforms coordinates from the unity coordinate system to the MQTT coordinate system */
    Vector3 InverseTransformCoordinates(Vector3 coords)
    {
        float temp = coords.y;
        coords.y = -coords.z;
        coords.z = temp;
        return coords;
    }

    /**Draws a line between two points: blue if no collisions red if collisions */
    void DrawLine(Vector3 start, Vector3 end)
    {
        GameObject connection = new GameObject();
        connection.transform.position = start;
        connection.AddComponent<LineRenderer>();
        LineRenderer lr = connection.GetComponent<LineRenderer>();
        if(Physics.CheckCapsule(start, end, flyRadius))
        {
            lr.material.color = Color.red;
            lineerrortimer = 1f;
            lineCollides = true;
        }else
        {
            lr.material.color = Color.blue;
        }
        lr.startWidth = 10f;
        lr.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        lr.SetPosition(0, start);
        lr.SetPosition(1, end);
    }

    /** draws lines between dynamically created waypoints */
    public void DrawAllLines()
    {
        lineCollides = false;
        for(int i=0; i<dynamicWaypoints.Count-1; i++)
        {
            GameObject w1 = (GameObject)dynamicWaypoints[i];
            GameObject w2 = (GameObject)dynamicWaypoints[i + 1];
            DrawLine(w1.transform.position, w2.transform.position);
        }
    }
    /**Draws lines to visualize trajectory and sends waypoint coordinates to a MQTT server if no collisions*/
    public void takeoff()
    {
        DrawAllLines();
        if (lineCollides == false)
        {
            //publish waypoint coordinates to the mqtt server on topic waypoints
            string waypointlocations = waypointsToString();
            client.Publish("waypoints", Encoding.UTF8.GetBytes(waypointlocations));
        }
    }

    /**makes a JSON formatted string containing all waypoint locations and ID in order */
    public string waypointsToString()
    {
        string locations = "{\n\t\"waypoints\": [\n";
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

    /**Adds a waypoint on specified coordinates (MQTT coordinates) */
    public void addDynamicWayPoint()
    {
        // position where it should go
        Vector3 coords = TransformCoordinates(new Vector3(x, y, z));
        //check if there already is something there
        if (Physics.CheckSphere(coords, flyRadius))
        {
            //if there is already something there
            waypointerrortimer = 1f;
        }else
        {
            waypointerrortimer = 0f;
            // if nothing there: put waypoint there
            GameObject waypoint = Instantiate(WayPoint, coords, Quaternion.identity);
            dynamicWaypoints.Add(waypoint);
        }
    }

    /**Changes x coordinate of new waypoint */
    public void changeX(string x)
    {
        this.x = int.Parse(x);
    }

    /**Changes y coordinate of new waypoint */
    public void changeY(string y)
    {
        this.y = int.Parse(y);
    }

    /**Changes z coordinate of new waypoint */
    public void changeZ(string z)
    {
        this.z = int.Parse(z);
    }
}
