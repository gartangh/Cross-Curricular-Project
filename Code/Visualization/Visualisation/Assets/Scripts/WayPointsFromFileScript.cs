using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class WayPointsFromFileScript : MonoBehaviour {
    public int x;
    public int y;
    public int z;
    float errordisplaytime;
    public bool coldetected;
    public GameObject WayPoint;
    public GUIStyle errorstyle;
    GameObject[] waypoints;
    ArrayList dynamicWaypoints = new ArrayList();


	// Use this for initialization
	void Start () {
        errordisplaytime = 0f;
        errorstyle.normal.textColor = Color.red;
        errorstyle.fontSize = 20;
        errorstyle.fontStyle = FontStyle.Italic;
    }
	
	// Update is called once per frame
	void Update () {
        // check if error should be displaying
        if (errordisplaytime > 0)
        {
            errordisplaytime -= Time.deltaTime;
        }
	}   

    void OnGUI ()
    {
        // display error
        if (Mathf.FloorToInt(errordisplaytime)>0)
        {
            GUI.Label(new Rect(50, 50, 100, 25), "Impossible!", errorstyle);
        }
    }

    /**Make waypoints from a file where they are specified as:
     x1,y1,z1
     x2,y2,z2
        in MQTT coordinate system coordinates
         */
    GameObject[] MakeWaypointsFromFile(string fileloc)
    {
        // create an array of strings with each element being a line from the file representing 1 waypoint's coordinates
        string[] positions = System.IO.File.ReadAllLines(fileloc);
        // create array to contain all waypoints
        GameObject[] waypoints = new GameObject[positions.Length];
        // instantiate all waypoints
        for (int i = 0; i < positions.Length; i++)
        {
            string[] position = positions[i].Split(',');
            float x = float.Parse(position[0]);
            float y = float.Parse(position[1]);
            float z = float.Parse(position[2]);
            // transform coordinates to unity coordinates
            Vector3 coords = TransformCoordinates(new Vector3(x, y, z));
            GameObject waypoint = Instantiate(WayPoint, coords, Quaternion.identity);
            waypoints[i] = waypoint;
        }
        return waypoints;
    }

    /**Writes locations of waypoints (in MQTT coordinates) to a file with location fileloc*/
    public void WriteWaypointsToFile(string fileloc)
    {
        // empty file if it should have existed before
        System.IO.File.Delete(fileloc);
        string[] lines = new string[dynamicWaypoints.Count];
        for(int i=0; i<dynamicWaypoints.Count; i++)
        {
            GameObject point = (GameObject)dynamicWaypoints[i];
            Vector3 coords = InverseTransformCoordinates(point.transform.position);
            string line = coords.x + "," + coords.y + "," + coords.z;
            lines[i] = line;
        }
        System.IO.File.AppendAllLines(fileloc, lines);
    }

    /**Transforms coordinates from the MQTT coordinate system to unity coordinate system */
    Vector3 TransformCoordinates(Vector3 coords)
    {
        float temp = coords.y;
        coords.x /= 1000;
        coords.y = coords.z / 1000;
        coords.z = -temp / 1000;
        return coords;
    }

    /**Transforms coordinates from the unity coordinate system to the MQTT coordinate system */
    Vector3 InverseTransformCoordinates(Vector3 coords)
    {
        coords *= 1000;
        float temp = coords.y;
        coords.y = -coords.z;
        coords.z = temp;
        return coords;
    }

    /**Draws a line between two points with a specific color */
    void DrawLine(Vector3 start, Vector3 end, Color color)
    {
        GameObject myLine = new GameObject();
        myLine.transform.position = start;
        myLine.AddComponent<LineRenderer>();
        LineRenderer lr = myLine.GetComponent<LineRenderer>();
        lr.material = new Material(Shader.Find("Particles/Alpha Blended Premultiply"));
        lr.SetColors(color, color);
        lr.SetWidth(0.01f, 0.01f);
        lr.SetPosition(0, start);
        lr.SetPosition(1, end);
    }

    /** draws lines between dynamically created waypoints */
    public void DrawAllLines()
    {
        for(int i=0; i<dynamicWaypoints.Count-1; i++)
        {
            GameObject w1 = (GameObject)dynamicWaypoints[i];
            GameObject w2 = (GameObject)dynamicWaypoints[i + 1];
            DrawLine(w1.transform.position, w2.transform.position, new Color(0, 0, 255));
        }
    }

    /**Adds a waypoint on specified coordinates */
    public void addWayPoint()
    {
        // position where it should go
        Vector3 coords = TransformCoordinates(new Vector3(x, y, z));
        //check if there already is something there
        SphereCollider col = (SphereCollider)WayPoint.GetComponent<Collider>();
        if (Physics.CheckSphere(coords, col.radius))
        {
            //if there is already something there
            errordisplaytime = 5f;
        }else
        {
            errordisplaytime = 0f;
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
