using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;

public class Pointer : MonoBehaviour
{
    public float m_Distance = 10.0f;
    public LineRenderer m_LineRenderer = null;
    public LayerMask m_EverythingMask = 0;
    public LayerMask m_InteractableMask = 0;
    public UnityAction<Vector3, GameObject> OnPointerUpdate = null;

    private Transform m_CurrentOrigin = null;
    private GameObject m_CurrentObject = null;

    private void Awake()
    {
        PlayerEvents.OnControllerSource += UpdateOrigin;
        PlayerEvents.OnTouchpadDown += ProcessTouchpadDown;
    }

    private void Start()
    {
        SetLineColor();
    }

    private void OnDestroy()
    {
        PlayerEvents.OnControllerSource -= UpdateOrigin;
        PlayerEvents.OnTouchpadDown -= ProcessTouchpadDown;
    }

    private void Update()
    {
        Vector3 hitPoint = UpdateLine();

        m_CurrentObject = UpdatePointerStatus();

        if (OnPointerUpdate != null) OnPointerUpdate(hitPoint, m_CurrentObject);
    }

    private Vector3 UpdateLine()
    {
        // Create Ray
        RaycastHit hit = CreateRaycast(m_EverythingMask);

        // Default end
        Vector3 endPosition = m_CurrentOrigin.position + (m_CurrentOrigin.forward * m_Distance);

        // Check hit
        if (hit.collider != null) endPosition = hit.point;

        // Set position of the line renderer
        m_LineRenderer.SetPosition(0, m_CurrentOrigin.position);
        m_LineRenderer.SetPosition(1, endPosition);

        return endPosition;
    }

    private void UpdateOrigin(OVRInput.Controller controller, GameObject controllerObject)
    {
        // Set origin of pointer
        m_CurrentOrigin = controllerObject.transform;

        // Is the laser visible?
        if(controller == OVRInput.Controller.Touchpad)
        {
            m_LineRenderer.enabled = false;
        }
        else
        {
            m_LineRenderer.enabled = true;
        }

    }

    private GameObject UpdatePointerStatus()
    {
        // Create ray
        RaycastHit hit = CreateRaycast(m_InteractableMask);

        // Check hit
        if (hit.collider) return hit.collider.gameObject;

        // Return
        return null;
    }

    private RaycastHit CreateRaycast(int layer)
    {
        RaycastHit hit;
        Ray ray = new Ray(m_CurrentOrigin.position, m_CurrentOrigin.forward);
        Physics.Raycast(ray, out hit, m_Distance, layer);

        return hit;
    }

    private void SetLineColor()
    {
        if (!m_LineRenderer) return;

        Color endColor = Color.white;
        endColor.a = 0.0f;

        m_LineRenderer.endColor = endColor;
    }

    private void ProcessTouchpadDown()
    {
        if (!m_CurrentObject) return;

        Interactable interactable = m_CurrentObject.GetComponent<Interactable>();
        interactable.Pressed();
    }
}
