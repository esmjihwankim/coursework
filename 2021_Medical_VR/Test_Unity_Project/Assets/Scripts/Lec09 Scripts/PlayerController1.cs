using System.Collections;
using System.Collections.Generic;
using UnityEngine;

public class PlayerController1 : MonoBehaviour
{
    public float speed;
    private Rigidbody rb;
    
    // Start is called before the first frame update
    void Start()
    {
        rb = GetComponent<Rigidbody>();
    }

    // Update is called once per frame
    void Update()
    {
        //float moveHorizontal = Input.GetAxis("Horizontal");
        //float moveVertical = Input.GetAxis("Vertical");

        Vector2 movement1 = OVRInput.Get(OVRInput.Axis2D.PrimaryTouchpad);

        Vector3 movement = new Vector3(movement1.x, 0.0f, movement1.y);

        rb.AddForce(movement * speed * Time.deltaTime);
    }
}
