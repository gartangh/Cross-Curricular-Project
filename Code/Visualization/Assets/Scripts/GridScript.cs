using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class GridScript : MonoBehaviour {
    public Material lineMaterial;

	// Use this for initialization
	void Start () {
        lineMaterial.SetPass(0);
        GL.PushMatrix();
        GL.Begin(GL.LINES);
        GL.Color(Color.blue);
        // Horizontal lines
        for (int i = 0; i < 30000; i +=60)
        {
            // draw line
            GL.Vertex3(i, 10, 0);
            GL.Vertex3(i, 10, 10000);
        }
        // Vertical lines
        for (int i=0; i<10000; i+=60)
        {
            GL.Vertex3(0, 0, i);
            GL.Vertex3(30000, 0, i);
        }
        GL.End();
        GL.PopMatrix();
	}
	
	// Update is called once per frame
	void Update () {
		
	}
}
