using System;
using System.Collections;
using System.Collections.Generic;
using System.Net;
using System.Text;
using UnityEngine;
using uPLibrary.Networking.M2Mqtt;
using uPLibrary.Networking.M2Mqtt.Messages;

public class DroneScript : MonoBehaviour {
    public MqttClient client;
    // ip-address of mqtt server
    public static IPAddress ip;
    public GameObject Drone;
    public static Dictionary<int, GameObject> droneDictionary = new Dictionary<int, GameObject>();
    // Topics to subscribe to
    static Dictionary<int, string> positionTopics = new Dictionary<int, string>();
    static Dictionary<int, string> heightTopics = new Dictionary<int, string>();
    static Dictionary<int, string> orientationTopics = new Dictionary<int, string>();
    // Placeholder for updated position, height & orientation
    static Dictionary<int, string> positions = new Dictionary<int, string>();
    static Dictionary<int, string> heights = new Dictionary<int, string>();
    static Dictionary<int, string> orientations = new Dictionary<int, string>();
    // Scale of the drone (default value)
    static int dronescale = 100;

    /** Message handling code */
    static void client_MqttMsgPublishReceived(object sender, MqttMsgPublishEventArgs e)
    {
        List<int> ids = new List<int>(droneDictionary.Keys);
        foreach(int id in ids)
        {
            if (e.Topic.Equals(positionTopics[id]))
            {
                positions[id] = Encoding.UTF8.GetString(e.Message);
            }
            else if (e.Topic.Equals(heightTopics[id]))
            {
                heights[id] = Encoding.UTF8.GetString(e.Message);
            }
            else if (e.Topic.Equals(orientationTopics[id]))
            {
                orientations[id] = Encoding.UTF8.GetString(e.Message);
            }
        }
    }

    /** Use this for initialization */
    void Start() {
        // Read config file for setup
        Setup();
        // Port is default port so doesnt have to be specified
        // 157.193.214.115 port 1883
        client = new MqttClient(ip);
        // Register to message received
        client.MqttMsgPublishReceived += client_MqttMsgPublishReceived;
        client.Connect(Guid.NewGuid().ToString());
        // Subscribe to vopposition, vopheight and voporientation topic for all id's
        List<int> ids = new List<int>(droneDictionary.Keys);
        foreach (int id in ids)
        {
            client.Subscribe(new string[] { positionTopics[id], heightTopics[id], orientationTopics[id] }, new byte[] { 0, 0, 0 });
        }
    }

    /** Update is called once per frame */
    void Update () {
        List<int> ids = new List<int>(droneDictionary.Keys);
        foreach (int id in ids)
        {
            // Update location
            droneDictionary[id].transform.position = TransformCoordinates(GetCoords(id));
            // Update orientation
            droneDictionary[id].transform.rotation = GetUnityOrientation(id);
        }
	}

    /** Transforms coordinates from the MQTT coordinate system to unity coordinate system */
    Vector3 TransformCoordinates(Vector3 coords)
    {
        float temp = coords.y;
        coords.y = coords.z;
        coords.z = -temp;

        return coords;
    }

    /** Gets coordinates from a string where they are as follows: "x,y,z"
     * and each decimal is indicated by a dot
     */
    Vector3 GetCoords (int id)
    {
        // Coords are seperated by a comma and decimals are indicated by a dot
        string[] coord = positions[id].Split(',');
        // Unity uses comma's instead of dot's for decimals
        float x = float.Parse(coord[0].Replace('.', ','));
        float y = float.Parse(coord[1].Replace('.', ','));
        float z = float.Parse(heights[id].Replace('.',','));

		return new Vector3(x, y, z);
    }

    /** Takes angles sent by drone and changes the rotation of the drone in unity*/
    Quaternion GetUnityOrientation(int id)
    {
		// Angles are seperated by a comma and decimals are indicated by a dot
        string[] angles = orientations[id].Split(',');
		// Unity uses comma's instead of dot's for decimals
        float heading = float.Parse(angles[0].Replace('.', ','))+90;
        float roll = -float.Parse(angles[1].Replace('.', ','));
        float pitch = float.Parse(angles[2].Replace('.', ','))+90;

		return Quaternion.Euler(roll, heading, pitch);
    }

    /** Reads config file and sets all variables accordingly */
    void Setup()
    {
        string[] config = System.IO.File.ReadAllLines(Application.dataPath + "/Config/Config.json");
        for(int i=0; i<config.Length; i++)
        {
            if (config[i].Contains("ip"))
            {
                string ipaddress = config[i].Split(':')[1].Split(',')[0].Split('"')[1];
                ip = IPAddress.Parse(ipaddress);

            }
            else if (config[i].Contains("dronescale"))
            {
                dronescale = Int32.Parse(config[i].Split(':')[1].Split('"')[1]);
            }
            else if (config[i].Contains("Drones"))
            {
                i++;
                // Instantiate all drones
                int id = 0;
                while (!config[i].Contains("]"))
                {
                    if (config[i].Contains("id"))
                    {
                        GameObject drone = Instantiate(Drone, new Vector3(0, i * 1000, 0), Quaternion.identity);
                        drone.transform.localScale = new Vector3(dronescale, dronescale, dronescale);
                        id = Int32.Parse(config[i].Split(':')[1].Split(',')[0].Split('"')[1]);
                        droneDictionary.Add(id, drone);
                        positions.Add(id, "0,0");
                        heights.Add(id,(id * 1000).ToString());
                        orientations.Add(id, "0,0,0");
                    }
                    else if (config[i].Contains("color"))
                    {
                        string color = config[i].Split(':')[1].Split(',')[0].Split('"')[1].Trim();
                        Color desiredColor = Color.black;
                        ColorUtility.TryParseHtmlString(color, out desiredColor);

                        // look for drone
                        GameObject drone = null;
                        droneDictionary.TryGetValue(id, out drone);
                        // set it's color
                        Renderer rend = drone.GetComponentInChildren<Renderer>();
                        rend.material.SetColor("_Color", desiredColor);
                    }
                    else if (config[i].Contains("positiontopic"))
                    {
                        string positiontopic = config[i].Split(':')[1].Split('"')[1].Trim();
                        positionTopics.Add(id, positiontopic);
                    }
                    else if (config[i].Contains("heighttopic"))
                    {
                        string heighttopic = config[i].Split(':')[1].Split('"')[1].Trim();
                        heightTopics.Add(id, heighttopic);
                    }
                    else if (config[i].Contains("orientationtopic"))
                    {
                        string orientationtopic = config[i].Split(':')[1].Split('"')[1].Trim();
                        orientationTopics.Add(id, orientationtopic);
                    }
                    i++;
                }
            }
        }
    }
}
